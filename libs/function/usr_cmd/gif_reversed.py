from asyncio import TimeoutError
from creart import create
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    SpacePolicy,
    WildcardMatch,
    RegexMatch,
    ParamMatch,
    ElementMatch,
)

from libs.control import Permission

from PIL import Image as PILImage
from PIL.Image import Image as PILImageType
from PIL import ImageSequence, ImageOps

# import requests
import aiohttp
from io import BytesIO
import time
import os
from loguru import logger
from typing import Tuple, List, Union
from collections import defaultdict
from random import randrange
from itertools import chain

from abc import ABC, abstractmethod

SMALL_IMG_DIM = 20
IMG_PROCESS_CACHE_PATH = "data/gif_reverse"


class ImgProcess:
    class TransparentAnimatedGifConverter(object):
        _PALETTE_SLOTSET = set(range(256))

        def __init__(
            self, img_rgba: PILImageType, alpha_threshold: int = 0
        ):
            self._img_rgba = img_rgba
            self._alpha_threshold = alpha_threshold

        def _process_pixels(self):
            """Set the transparent pixels to the color 0."""
            self._transparent_pixels = set(
                idx
                for idx, alpha in enumerate(
                    self._img_rgba.getchannel(channel="A").getdata()
                )
                if alpha <= self._alpha_threshold
            )

        def _set_parsed_palette(self):
            """Parse the RGB palette color `tuple`s from the palette."""
            palette = self._img_p.getpalette()
            self._img_p_used_palette_idxs = set(
                idx
                for pal_idx, idx in enumerate(self._img_p_data)
                if pal_idx not in self._transparent_pixels
            )
            self._img_p_parsedpalette = dict(
                (idx, tuple(palette[idx * 3 : idx * 3 + 3]))
                for idx in self._img_p_used_palette_idxs
            )

        def _get_similar_color_idx(self):
            """Return a palette index with the closest similar color."""
            old_color = self._img_p_parsedpalette[0]
            dict_distance = defaultdict(list)
            for idx in range(1, 256):
                color_item = self._img_p_parsedpalette[idx]
                if color_item == old_color:
                    return idx
                distance = sum(
                    (
                        abs(old_color[0] - color_item[0]),  # Red
                        abs(old_color[1] - color_item[1]),  # Green
                        abs(old_color[2] - color_item[2]),
                    )
                )  # Blue
                dict_distance[distance].append(idx)
            return dict_distance[sorted(dict_distance)[0]][0]

        def _remap_palette_idx_zero(self):
            """Since the first color is used in the palette, remap it."""
            free_slots = (
                self._PALETTE_SLOTSET - self._img_p_used_palette_idxs
            )
            new_idx = (
                free_slots.pop()
                if free_slots
                else self._get_similar_color_idx()
            )
            self._img_p_used_palette_idxs.add(new_idx)
            self._palette_replaces["idx_from"].append(0)
            self._palette_replaces["idx_to"].append(new_idx)
            self._img_p_parsedpalette[
                new_idx
            ] = self._img_p_parsedpalette[0]
            del self._img_p_parsedpalette[0]

        def _get_unused_color(self) -> tuple:
            """Return a color for the palette that does not collide with any other already in the palette."""
            used_colors = set(self._img_p_parsedpalette.values())
            while True:
                new_color = (
                    randrange(256),
                    randrange(256),
                    randrange(256),
                )
                if new_color not in used_colors:
                    return new_color

        def _process_palette(self):
            """Adjust palette to have the zeroth color set as transparent. Basically, get another palette
            index for the zeroth color."""
            self._set_parsed_palette()
            if 0 in self._img_p_used_palette_idxs:
                self._remap_palette_idx_zero()
            self._img_p_parsedpalette[0] = self._get_unused_color()

        def _adjust_pixels(self):
            """Convert the pixels into their new values."""
            if self._palette_replaces["idx_from"]:
                trans_table = bytearray.maketrans(
                    bytes(self._palette_replaces["idx_from"]),
                    bytes(self._palette_replaces["idx_to"]),
                )
                self._img_p_data = self._img_p_data.translate(
                    trans_table
                )
            for idx_pixel in self._transparent_pixels:
                self._img_p_data[idx_pixel] = 0
            self._img_p.frombytes(data=bytes(self._img_p_data))

        def _adjust_palette(self):
            """Modify the palette in the new `Image`."""
            unused_color = self._get_unused_color()
            final_palette = chain.from_iterable(
                self._img_p_parsedpalette.get(x, unused_color)
                for x in range(256)
            )
            self._img_p.putpalette(data=final_palette)

        def process(self) -> PILImageType:
            """Return the processed mode `P` `Image`."""
            self._img_p = self._img_rgba.convert(mode="P")
            self._img_p_data = bytearray(self._img_p.tobytes())
            self._palette_replaces = dict(
                idx_from=list(), idx_to=list()
            )
            self._process_pixels()
            self._process_palette()
            self._adjust_pixels()
            self._adjust_palette()
            self._img_p.info["transparency"] = 0
            self._img_p.info["background"] = 0
            return self._img_p

    @classmethod
    def _create_animated_gif(
        cls,
        images: List[PILImageType],
        durations: Union[int, List[int]],
    ) -> Tuple[PILImageType, dict]:
        """If the image is a GIF, create an its thumbnail here."""
        save_kwargs = dict()
        new_images: List[PILImageType] = []

        for frame in images:
            thumbnail = frame.copy()  # type: Image
            thumbnail_rgba = thumbnail.convert(mode="RGBA")
            thumbnail_rgba.thumbnail(size=frame.size, reducing_gap=3.0)
            converter = cls.TransparentAnimatedGifConverter(
                img_rgba=thumbnail_rgba
            )
            thumbnail_p = converter.process()  # type: Image
            new_images.append(thumbnail_p)

        output_image = new_images[0]
        save_kwargs.update(
            format="GIF",
            save_all=True,
            optimize=False,
            append_images=new_images[1:],
            duration=durations,
            disposal=2,  # Other disposals don't work
            loop=0,
        )
        return output_image, save_kwargs

    @classmethod
    def save_transparent_gif(
        cls,
        images: List[PILImageType],
        durations: Union[int, List[int]],
        save_file,
    ):
        """Creates a transparent GIF, adjusting to avoid transparency issues that are present in the PIL library

        Note that this does NOT work for partial alpha. The partial alpha gets discarded and replaced by solid colors.

        Parameters:
            images: a list of PIL Image objects that compose the GIF frames
            durations: an int or List[int] that describes the animation durations for the frames of this GIF
            save_file: A filename (string), pathlib.Path object or file object. (This parameter corresponds
                    and is passed to the PIL.Image.save() method.)
        Returns:
            Image - The PIL Image object (after first saving the image to the specified target)
        """
        root_frame, save_args = cls._create_animated_gif(
            images, durations
        )
        root_frame.save(save_file, **save_args)

    class AbsImgProcessFactory(ABC):
        @classmethod
        @abstractmethod
        def process_static_img(cls, img: PILImageType) -> PILImageType:
            """Process a static image"""

        @classmethod
        def process_gif_img(
            cls, img: PILImageType, *args
        ) -> tuple[list[int], list[PILImageType]]:
            """Process a gif image"""
            duration = []
            sequence = []
            for i in ImageSequence.Iterator(img):
                duration.append(i.info["duration"])
                new_i = cls.process_static_img(i, *args)
                sequence.append(new_i)
            return duration, sequence

    class ImgExport:
        @classmethod
        def generate_default_filename(cls, fmt: str) -> str:
            req_id = str(int(time.time()))
            file_path = f"{IMG_PROCESS_CACHE_PATH}/{req_id}.{fmt}"
            return file_path

        @classmethod
        def export_static_img(
            cls, img: PILImageType, path: str = ""
        ) -> str:
            """Save and export the path of a static image"""
            if len(path) == 0:
                path = (
                    cls.generate_default_filename(img.format)
                    if img.format is str
                    else cls.generate_default_filename("PNG")
                )

            img.save(path)
            return path

        @classmethod
        def export_gif_img(
            cls,
            img_seq: list[PILImageType],
            dur_seq: list[int],
            path: str = "",
        ) -> str:
            """Save and export the path of a gif image"""
            if len(path) == 0:
                path = cls.generate_default_filename("GIF")
            ImgProcess.save_transparent_gif(img_seq, dur_seq, path)
            return path

    @classmethod
    def is_all_ratio_valid(cls, *args):
        for arg in args:
            if not isinstance(arg, float):
                return False
            if arg < 0.0 or arg > 1.0:
                return False
        if len(args) != len(set(args)):
            return False
        return True

    class ImgReverseFactory(AbsImgProcessFactory):
        @classmethod
        def process_static_img(cls, img: PILImageType) -> PILImageType:
            raise NotImplementedError(
                "You cannot reverse a static image"
            )

        @classmethod
        def process_gif_img(
            cls, img: PILImageType
        ) -> tuple[list[int], list[PILImageType]]:
            duration = []
            sequence = []
            for i in ImageSequence.Iterator(img):
                duration.append(i.info["duration"])
                sequence.append(i.copy())
            duration.reverse()
            sequence.reverse()
            return duration, sequence

    class ImgMirrorFactory(AbsImgProcessFactory):
        @classmethod
        def process_static_img(cls, img: PILImageType) -> PILImageType:
            new_img = ImageOps.mirror(img)
            return new_img

    class ImgLeftMirrorFactory(AbsImgProcessFactory):
        @classmethod
        def process_static_img(
            cls,
            img: PILImageType,
            slice_r_ratio: float = 0.5,
            slice_l_ratio: float = 0.0,
        ) -> PILImageType:
            if not ImgProcess.is_all_ratio_valid(
                slice_l_ratio, slice_r_ratio
            ):
                raise ValueError

            if slice_l_ratio > slice_r_ratio:
                slice_l_ratio, slice_r_ratio = (
                    slice_r_ratio,
                    slice_l_ratio,
                )
            width, height = img.size
            l = round(slice_l_ratio * width)
            r = round(slice_r_ratio * width)
            if abs(l - r) <= 0:
                raise ValueError

            l_half = img.crop((l, 0, r, height))
            r_half = ImageOps.mirror(l_half)
            new_img = PILImage.new(
                "RGBA", ((r - l) * 2, height), (255, 255, 255, 0)
            )
            new_img.paste(l_half, (0, 0))
            new_img.paste(r_half, (r - l, 0))
            return new_img

    class ImgRightMirrorFactory(AbsImgProcessFactory):
        @classmethod
        def process_static_img(
            cls,
            img: PILImageType,
            slice_l_ratio: float = 0.5,
            slice_r_ratio: float = 1.0,
        ) -> PILImageType:
            if not ImgProcess.is_all_ratio_valid(
                slice_l_ratio, slice_r_ratio
            ):
                raise ValueError

            if slice_l_ratio > slice_r_ratio:
                slice_l_ratio, slice_r_ratio = (
                    slice_r_ratio,
                    slice_l_ratio,
                )
            width, height = img.size
            l = round(slice_l_ratio * width)
            r = round(slice_r_ratio * width)
            if abs(l - r) <= 0:
                raise ValueError

            r_half = img.crop((l, 0, r, height))
            l_half = ImageOps.mirror(r_half)
            new_img = PILImage.new(
                "RGBA", ((r - l) * 2, height), (255, 255, 255, 0)
            )
            new_img.paste(l_half, (0, 0))
            new_img.paste(r_half, (r - l, 0))
            return new_img

    class ImgCompressFactory(AbsImgProcessFactory):
        @classmethod
        def process_static_img(cls, img: PILImageType) -> PILImageType:
            width, height = img.size
            if width >= height:
                new_size = (
                    int(width / height * SMALL_IMG_DIM),
                    SMALL_IMG_DIM,
                )
            else:
                new_size = (
                    SMALL_IMG_DIM,
                    int(height / width * SMALL_IMG_DIM),
                )
            new_img = img.copy().resize(new_size)
            return new_img

    factory_name_dict = {
        "倒放": ImgReverseFactory,
        "镜像": ImgMirrorFactory,
        "左镜像": ImgLeftMirrorFactory,
        "右镜像": ImgRightMirrorFactory,
        "小": ImgCompressFactory,
    }

    factory_optional_args = {
        ImgReverseFactory: [],
        ImgMirrorFactory: [],
        ImgLeftMirrorFactory: [float, float],
        ImgRightMirrorFactory: [float, float],
        ImgCompressFactory: [],
    }

    @classmethod
    def process_image(
        cls, img: PILImageType, op: str, args_str: str
    ) -> str:
        if op not in cls.factory_name_dict.keys():
            raise NotImplementedError(f"No Such Image Operation {op}")
        img_process_factory = cls.factory_name_dict[op]

        args_strs = args_str.strip().split()
        args_list = cls.factory_optional_args[img_process_factory]
        args = []
        for idx, type in enumerate(args_list):
            try:
                args.append(type(args_strs[idx]))
            except Exception:
                continue

        if not img.format == "GIF":
            processed_img = img_process_factory.process_static_img(
                img, *args
            )
            file_path = cls.ImgExport.export_static_img(processed_img)
        else:
            dur, seq = img_process_factory.process_gif_img(img, *args)
            file_path = cls.ImgExport.export_gif_img(seq, dur)
        return file_path

    @classmethod
    def get_operation(cls, s: str) -> str:
        for k in cls.factory_name_dict.keys():
            if s.startswith(k):
                return k
        return ""


inc = create(InterruptControl)

channel = Channel.current()

channel.name("img_cmd")
channel.description("图片处理命令模组")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
        inline_dispatchers=[
            Twilight(
                FullMatch("/").space(SpacePolicy.NOSPACE),
                "op" @ ParamMatch().space(SpacePolicy.PRESERVE),
                "optional_args_regexresult"
                @ RegexMatch(r"((\d+.?\d*) ?)+", optional=True).space(
                    SpacePolicy.PRESERVE
                ),
                "tgt_img" @ ElementMatch(Image, optional=True),
            )
        ],
    )
)
async def img_process(
    app: Ariadne,
    member: Member,
    group: Group,
    message: MessageChain,
    op: RegexResult,
    optional_args_regexresult: RegexResult,
):
    if not op.matched:
        await app.send_group_message(group, MessageChain("请重新输入指令"))
        raise ExecutionStop
    if op.result is None:
        operation = ""
    else:
        operation = ImgProcess.get_operation(op.result.display.strip())
    logger.info(f"The opertion is {operation}")
    if operation == "":
        # await app.send_group_message(group, MessageChain("您输入的指令暂不支持哦"))
        raise ExecutionStop
    if Image not in message:

        @Waiter.create_using_function([GroupMessage])
        async def shop_water(g: Group, m: Member, msg: MessageChain):
            if group.id == g.id and member.id == m.id:
                return msg

        try:
            ret_msg = await inc.wait(shop_water, timeout=30)
            if Image not in ret_msg:
                await app.send_group_message(
                    group, MessageChain("你没发图啊")
                )
                raise ExecutionStop
            img_elements = ret_msg.get(Image)
        except TimeoutError:
            logger.info(f"shop timeout by {member.id}")
            raise ExecutionStop
    else:
        img_elements = message.get(Image)

    target_img_url = img_elements[0].url
    logger.info(target_img_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(target_img_url) as response:
            img_data = await response.read()
    target_img = PILImage.open(BytesIO(img_data))
    if optional_args_regexresult.result is None:
        optional_args = ""
    else:
        optional_args = optional_args_regexresult.result.display
    try:
        path_after_process = ImgProcess.process_image(
            target_img, operation, optional_args
        )
    except ValueError:
        await app.send_group_message(
            group,
            MessageChain("数值不对啊，重新填吧！"),
        )
        raise ExecutionStop

    await app.send_group_message(
        group,
        MessageChain([Image(path=path_after_process)]),
    )

    os.remove(path_after_process)
