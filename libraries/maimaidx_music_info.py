import copy

from .. import MessageSegment, get_botname
from .image import rounded_corners
from .maimai_best_50 import *
from .maimaidx_music import Music, mai


def open_rgba(path):
    return Image.open(path).convert("RGBA")


async def draw_plate_table(qqid: int, version: str, plan: str) -> Union[MessageSegment, str]:
    """
    绘制完成表
    """
    try:
        if version in platecn:
            version = platecn[version]

        ver, _ver = version_map.get(version, ([plate_to_dx_version[version]], version))

        music_id_list = mai.total_plate_id_list[_ver]
        music = mai.total_list.by_id_list(music_id_list)
        plate_total_num = len(music_id_list)

        playerdata: List[PlayInfoDefault] = []

        obj = await maiApi.query_user_plate(qqid=qqid, version=ver)

        for _d in obj:
            if _d.song_id not in music_id_list:
                continue
            _music = mai.total_list.by_id(_d.song_id)
            _d.table_level = _music.level
            _d.ds = _music.ds[_d.level_index]
            playerdata.append(_d)

        ra: Dict[str, Dict[str, List[Optional[PlayInfoDefault]]]] = {}

        music.sort(key=lambda x: x.ds[3], reverse=True)

        number = 4 if version not in ['霸', '舞'] else 5

        for _m in music:
            if _m.level[3] not in ra:
                ra[_m.level[3]] = {}
            ra[_m.level[3]][str(_m.id)] = [None for _ in range(number)]

        for _d in playerdata:
            if number == 4 and _d.level_index == 4:
                continue
            ra[_d.table_level[3]][str(_d.song_id)][_d.level_index] = _d

        finished_bg = [open_rgba(maimaidir / f't-{_}.png') for _ in range(4)]
        unfinished_bg = open_rgba(maimaidir / 'unfinished_bg_2.png')
        complete_bg = open_rgba(maimaidir / 'complete_bg_2.png')

        # 背景
        im = open_rgba(platedir / 'plate_bg.png')
        draw = ImageDraw.Draw(im)
        tr = DrawText(draw, TBFONT)
        mr = DrawText(draw, SIYUAN)

        # plate num
        im.alpha_composite(
            open_rgba(maimaidir / 'plate_num.png'),
            (185, 20)
        )

        # 顶部横幅
        im.alpha_composite(
            open_rgba(
                platedir / f'{version}{"極" if plan == "极" else plan}.png'
            ).resize((1000, 161)),
            (200, 35)
        )

        lv: List[set[int]] = [set() for _ in range(number)]
        y = 245

        # ===================== 极 / 极系 =====================
        if plan in ['极', '極']:
            for level in ra:
                x = 200
                y += 15

                for num, _id in enumerate(ra[level]):
                    if num % 10 == 0:
                        x = 200
                        y += 115
                    else:
                        x += 115

                    f: List[int] = []

                    for n, play in enumerate(ra[level][_id]):
                        if play is None or not getattr(play, "fc", None):
                            continue

                        if n == 3:
                            im.alpha_composite(complete_bg, (x, y))
                            fc = open_rgba(
                                maimaidir / f'UI_CHR_PlayBonus_{fcl[play.fc]}.png'
                            ).resize((75, 75))
                            im.alpha_composite(fc, (x + 13, y + 3))

                        lv[n].add(play.song_id)
                        f.append(n)

                    for n in f:
                        im.alpha_composite(
                            finished_bg[n],
                            (x + 5 + 25 * n, y + 67)
                        )

        # ===================== 将 =====================
        if plan == '将':
            for level in ra:
                x = 200
                y += 15

                for num, _id in enumerate(ra[level]):
                    if num % 10 == 0:
                        x = 200
                        y += 115
                    else:
                        x += 115

                    f: List[int] = []

                    for n, play in enumerate(ra[level][_id]):
                        if play is None or play.achievements < 100:
                            continue

                        if n == 3:
                            im.alpha_composite(
                                complete_bg if play.achievements >= 100 else unfinished_bg,
                                (x, y)
                            )

                            rate = computeRa(play.ds, play.achievements, onlyrate=True)
                            rank = open_rgba(
                                maimaidir / f'UI_TTR_Rank_{rate}.png'
                            ).resize((102, 46))

                            im.alpha_composite(rank, (x - 1, y + 15))

                        lv[n].add(play.song_id)
                        f.append(n)

                    for n in f:
                        im.alpha_composite(
                            finished_bg[n],
                            (x + 5 + 25 * n, y + 67)
                        )

        # ===================== 神 =====================
        if plan == '神':
            _fc = ['ap', 'app']

            for level in ra:
                x = 200
                y += 15

                for num, _id in enumerate(ra[level]):
                    if num % 10 == 0:
                        x = 200
                        y += 115
                    else:
                        x += 115

                    f: List[int] = []

                    for n, play in enumerate(ra[level][_id]):
                        if play is None or play.fc not in _fc:
                            continue

                        if n == 3:
                            im.alpha_composite(complete_bg, (x, y))
                            ap = open_rgba(
                                maimaidir / f'UI_CHR_PlayBonus_{fcl[play.fc]}.png'
                            ).resize((75, 75))
                            im.alpha_composite(ap, (x + 13, y + 3))

                        lv[n].add(play.song_id)
                        f.append(n)

                    for n in f:
                        im.alpha_composite(
                            finished_bg[n],
                            (x + 5 + 25 * n, y + 67)
                        )

        # ===================== 舞舞 =====================
        if plan == '舞舞':
            fs = ['fsd', 'fdx', 'fsdp', 'fdxp']

            for level in ra:
                x = 200
                y += 15

                for num, _id in enumerate(ra[level]):
                    if num % 10 == 0:
                        x = 200
                        y += 115
                    else:
                        x += 115

                    f: List[int] = []

                    for n, play in enumerate(ra[level][_id]):
                        if play is None or play.fs not in fs:
                            continue

                        if n == 3:
                            im.alpha_composite(complete_bg, (x, y))
                            fsd = open_rgba(
                                maimaidir / f'UI_CHR_PlayBonus_{fsl[play.fs]}.png'
                            ).resize((75, 75))
                            im.alpha_composite(fsd, (x + 13, y + 3))

                        lv[n].add(play.song_id)
                        f.append(n)

                    for n in f:
                        im.alpha_composite(
                            finished_bg[n],
                            (x + 5 + 25 * n, y + 67)
                        )

        # ===================== 统计 =====================
        color = ScoreBaseImage.id_color.copy()
        color.insert(0, (124, 129, 255, 255))

        for num in range(len(lv) + 1):
            if num == 0:
                v = set.intersection(*lv)
                _v = f'{len(v)}/{plate_total_num}'
            else:
                _v = len(lv[num - 1])

            if _v == plate_total_num:
                mr.draw(390 + 200 * num, 270, 35, '完成', color[num], 'rm', 4, (255, 255, 255, 255))
            else:
                tr.draw(390 + 200 * num, 270, 40, _v, color[num], 'rm', 4, (255, 255, 255, 255))

        return MessageSegment.image(image_to_base64(im))

    except (
        UserNotFoundError,
        UserNotExistsError,
        UserDisabledQueryError,
        TokenError,
        TokenDisableError,
        TokenNotFoundError,
    ) as e:
        return str(e)

    except Exception as e:
        log.error(traceback.format_exc())
        return f'未知错误：{type(e)}\n请联系Bot管理员'
