from PIL import Image as IMG
import aiohttp
from io import BytesIO

def generate_avatar_with_flag(avatar_fs, target_path: str = 'data/avatar/result.png'):
    avatar = avatar_fs
    flag = IMG.open('data/avatar/flag.png')

    w,h = avatar.size
    canvas = flag.resize((w,h))
    avatar.paste(canvas, (0, 0), canvas)
    avatar.save(target_path)
    
    return target_path

async def get_qq_avatar(mem_id: int):
    '''return the image file stream based on qq id'''
    url = f'http://q1.qlogo.cn/g?b=qq&nk={str(mem_id)}&s=640'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            img_content = await resp.read()

    return IMG.open(BytesIO(img_content)).convert("RGBA")