from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
ASSET_DIR = ROOT / "tmp" / "pdfs" / "guide_assets"
MANUAL_IMG_DIR = ROOT / "tmp" / "pdfs"
OUT_PDF = OUT_DIR / "无线DAP调试器_Keil5使用指南_STM32F103RCT6_MSPM0G3507.pdf"


def setup_fonts():
    font_regular = r"C:\Windows\Fonts\msyh.ttc"
    font_bold = r"C:\Windows\Fonts\msyhbd.ttc"
    pdfmetrics.registerFont(TTFont("MSYH", font_regular))
    pdfmetrics.registerFont(TTFont("MSYH-Bold", font_bold))


def crop_asset(src_name, box, out_name):
    src = MANUAL_IMG_DIR / src_name
    dst = ASSET_DIR / out_name
    if not src.exists():
        return None
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    img = PILImage.open(src).convert("RGB")
    cropped = img.crop(box)
    cropped.save(dst, quality=92)
    return dst


def prepare_assets():
    assets = {}
    assets["pinout"] = crop_asset("manual-05.png", (560, 600, 1465, 1135), "dap_pinout.png")
    assets["conf"] = crop_asset("manual-06.png", (720, 900, 1540, 1825), "conf_txt.png")
    assets["topology"] = crop_asset("manual-08.png", (380, 250, 1420, 995), "wireless_topology.png")
    assets["swd_jtag"] = crop_asset("manual-09.png", (360, 290, 1505, 1285), "swd_jtag.png")
    assets["keil_select"] = crop_asset("manual-12.png", (380, 240, 1495, 1235), "keil_debug_select.png")
    assets["keil_flash"] = crop_asset("manual-13.png", (280, 315, 1650, 1935), "keil_flash_download.png")
    return assets


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="MSYH-Bold",
            fontSize=24,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#153B5B"),
            wordWrap="CJK",
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontName="MSYH",
            fontSize=11,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="MSYH-Bold",
            fontSize=18,
            leading=24,
            spaceBefore=4,
            spaceAfter=8,
            textColor=colors.HexColor("#0F2F49"),
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="MSYH-Bold",
            fontSize=13,
            leading=18,
            spaceBefore=8,
            spaceAfter=5,
            textColor=colors.HexColor("#164A6B"),
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="MSYH",
            fontSize=9.6,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#20242A"),
            wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="MSYH",
            fontSize=8.1,
            leading=12,
            textColor=colors.HexColor("#4B5563"),
            wordWrap="CJK",
        ),
        "note": ParagraphStyle(
            "note",
            parent=base["Normal"],
            fontName="MSYH",
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#5F370E"),
            backColor=colors.HexColor("#FFF7E6"),
            borderColor=colors.HexColor("#F0C36A"),
            borderWidth=0.7,
            borderPadding=6,
            wordWrap="CJK",
        ),
        "danger": ParagraphStyle(
            "danger",
            parent=base["Normal"],
            fontName="MSYH-Bold",
            fontSize=9,
            leading=14,
            textColor=colors.HexColor("#7A1B1B"),
            backColor=colors.HexColor("#FFF1F1"),
            borderColor=colors.HexColor("#E8A0A0"),
            borderWidth=0.7,
            borderPadding=6,
            wordWrap="CJK",
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#111827"),
        ),
    }


def p(text, style):
    return Paragraph(text, style)


def tcell(text, style):
    return Paragraph(str(text), style)


def styled_table(data, col_widths=None, header=True, font_size=None):
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0, hAlign="LEFT")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "MSYH"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size or 8.3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DCE3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEAF5")),
                ("FONTNAME", (0, 0), (-1, 0), "MSYH-Bold"),
            ]
        )
    for row in range(1 if header else 0, len(data)):
        if row % 2 == 0:
            style.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor("#F7FAFC")))
    table.setStyle(TableStyle(style))
    return table


def image_flow(path, width_mm, max_height_mm=None):
    if not path or not Path(path).exists():
        return None
    img = PILImage.open(path)
    w_px, h_px = img.size
    width = width_mm * mm
    height = width * h_px / w_px
    if max_height_mm and height > max_height_mm * mm:
        height = max_height_mm * mm
        width = height * w_px / h_px
    flow = Image(str(path), width=width, height=height)
    flow.hAlign = "CENTER"
    return flow


def keep(items):
    return [x for x in items if x is not None]


def connector_table(styles):
    data = [
        [tcell("<b>左列</b>", styles["body"]), tcell("<b>右列</b>", styles["body"])],
        [tcell("5V", styles["body"]), tcell("TX", styles["body"])],
        [tcell("3V3", styles["body"]), tcell("RX", styles["body"])],
        [tcell("GND", styles["body"]), tcell("RST", styles["body"])],
        [tcell("CLK", styles["body"]), tcell("TDI", styles["body"])],
        [tcell("DIO", styles["body"]), tcell("TDO", styles["body"])],
        [tcell("DIR", styles["body"]), tcell("GND", styles["body"])],
    ]
    table = Table(data, colWidths=[32 * mm, 32 * mm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "MSYH-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#A8B7C7")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEAF5")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#EAF2F8")),
                ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#DDF7E7")),
                ("BACKGROUND", (0, 4), (0, 5), colors.HexColor("#FFF3C4")),
                ("BACKGROUND", (1, 3), (1, 3), colors.HexColor("#FFE2E2")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def bullet_list(items, styles):
    data = []
    for item in items:
        data.append([Paragraph("•", styles["body"]), Paragraph(item, styles["body"])])
    tbl = Table(data, colWidths=[5 * mm, 160 * mm], hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ]
        )
    )
    return tbl


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("MSYH", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(18 * mm, h - 12 * mm, "塔克无线高速 DAP 调试下载器 - Keil5 使用指南")
    canvas.drawRightString(w - 18 * mm, 10 * mm, f"{doc.page}")
    canvas.setStrokeColor(colors.HexColor("#D5DCE3"))
    canvas.line(18 * mm, h - 15 * mm, w - 18 * mm, h - 15 * mm)
    canvas.restoreState()


def add_title_page(story, styles, assets):
    story += [
        Spacer(1, 18 * mm),
        p("无线高速 DAP 调试下载器<br/>Keil5 烧录使用指南", styles["title"]),
        Spacer(1, 4 * mm),
        p("适用目标：STM32F103RCT6、MSPM0G3507。适用方式：有线 CMSIS-DAP 或无线 Host/Slave 模式。", styles["subtitle"]),
        Spacer(1, 10 * mm),
    ]
    img = image_flow(assets.get("topology"), 138, 78)
    if img:
        story.append(img)
        story.append(Spacer(1, 5 * mm))
    quick = [
        [tcell("先做什么", styles["body"]), tcell("要点", styles["body"])],
        [tcell("1. 确认模式", styles["body"]), tcell("有线模式红灯；无线 PC 端蓝灯 Host；目标板端绿灯 Slave。", styles["body"])],
        [tcell("2. 接 SWD", styles["body"]), tcell("CLK 接 SWCLK，DIO 接 SWDIO，GND 必接，RST 推荐接。", styles["body"])],
        [tcell("3. 打开 Keil5", styles["body"]), tcell("Debug 选择 CMSIS-DAP Debugger，Settings 中 Port 选择 SW。", styles["body"])],
        [tcell("4. 配 Flash 算法", styles["body"]), tcell("STM32 选对应 F1 Flash；MSPM0 只选 MAIN Flash，避免误动 NONMAIN。", styles["body"])],
    ]
    story.append(styled_table(quick, [35 * mm, 125 * mm]))
    story += [
        Spacer(1, 7 * mm),
        p("重要提醒：裸芯片或 3.3V 最小系统不要把 5V 直接接到 MCU VDD。仅当目标板有 5V 输入和稳压电路时，才可用调试器/目标板的 5V 线。", styles["danger"]),
        Spacer(1, 8 * mm),
        p("资料来源：本地《塔克 l 无线高速DAP调试下载器手册 V3.0.1》、ST STM32F103RC 官方数据手册、TI MSPM0G3507 官方数据手册、TI MSPM0 Keil QuickStart。", styles["small"]),
        PageBreak(),
    ]


def add_modes_page(story, styles, assets):
    story.append(p("1. 调试器模式与无线配对", styles["h1"]))
    story.append(p("这套调试器分为 PC 端和目标板端。普通款模块硬件一致，可以通过按键或 U 盘配置文件切换为有线、无线主机、无线从机。", styles["body"]))
    story.append(Spacer(1, 4 * mm))
    mode_table = [
        [tcell("状态", styles["body"]), tcell("指示灯", styles["body"]), tcell("用途", styles["body"])],
        [tcell("有线模式 USB", styles["body"]), tcell("红色", styles["body"]), tcell("单个调试器直接接电脑和目标板，速度较高。", styles["body"])],
        [tcell("无线主机 Host", styles["body"]), tcell("蓝色", styles["body"]), tcell("插电脑 USB，Keil 识别为 CMSIS-DAP。", styles["body"])],
        [tcell("无线从机 Slave", styles["body"]), tcell("绿色", styles["body"]), tcell("接目标板 SWD/JTAG/串口，由目标板供电。", styles["body"])],
        [tcell("配对中", styles["body"]), tcell("紫色慢闪", styles["body"]), tcell("两个模块按 KB 上电进入自动配对。", styles["body"])],
    ]
    story.append(styled_table(mode_table, [36 * mm, 25 * mm, 99 * mm]))
    story.append(Spacer(1, 5 * mm))
    story.append(p("按键设置", styles["h2"]))
    story.append(
        bullet_list(
            [
                "长按 KA 至指示灯变黄，再短按 KA 循环切换模式；调到需要的颜色后长按 KA 保存，重新上电生效。",
                "配对时两个模块都按住 KB 上电，约 2 秒松开；当两个模块自动变成蓝灯和绿灯后，重新上电使用。",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p("U 盘配置", styles["h2"]))
    story.append(
        p(
            "数据线连接电脑后会出现 U 盘，修改 <b>CONF.TXT</b> 后保存并重新上电。无线使用时 PC 端设置 <b>mode=master</b>，目标端设置 <b>mode=slave</b>，两端 <b>addr</b> 必须完全一致。",
            styles["body"],
        )
    )
    conf_data = [
        [tcell("参数", styles["body"]), tcell("建议值/说明", styles["body"])],
        [tcell("mode", styles["body"]), tcell("usb = 有线；master = 无线主机；slave = 无线从机。", styles["body"])],
        [tcell("addr", styles["body"]), tcell("8 位十六进制同步地址；主从必须一致。", styles["body"])],
        [tcell("rate", styles["body"]), tcell("2M、1M、500K、125K；速率越低距离越远、越稳。", styles["body"])],
        [tcell("esp_down", styles["body"]), tcell("ESP 下载模式，本指南烧录 STM32/MSPM0 时保持 disable。", styles["body"])],
    ]
    story.append(styled_table(conf_data, [32 * mm, 128 * mm]))
    img = image_flow(assets.get("conf"), 108, 62)
    if img:
        story.append(Spacer(1, 5 * mm))
        story.append(img)
    story.append(PageBreak())


def add_wiring_common(story, styles, assets):
    story.append(p("2. 接线总览", styles["h1"]))
    intro = "SWD 是本指南推荐接口，线少、稳定，STM32F103RCT6 和 MSPM0G3507 都支持。JTAG 通常不需要，除非项目明确要求。"
    story.append(p(intro, styles["body"]))
    story.append(Spacer(1, 4 * mm))
    pinout_layout = Table(
        [[connector_table(styles), image_flow(assets.get("pinout"), 88, 55)]],
        colWidths=[72 * mm, 88 * mm],
        hAlign="LEFT",
    )
    pinout_layout.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(pinout_layout)
    story.append(Spacer(1, 5 * mm))
    swd = [
        [tcell("调试器", styles["body"]), tcell("目标板", styles["body"]), tcell("作用", styles["body"]), tcell("是否必须", styles["body"])],
        [tcell("CLK", styles["body"]), tcell("SWCLK/TCK", styles["body"]), tcell("SWD 时钟", styles["body"]), tcell("必须", styles["body"])],
        [tcell("DIO", styles["body"]), tcell("SWDIO/TMS", styles["body"]), tcell("SWD 双向数据", styles["body"]), tcell("必须", styles["body"])],
        [tcell("GND", styles["body"]), tcell("GND", styles["body"]), tcell("共地", styles["body"]), tcell("必须", styles["body"])],
        [tcell("RST", styles["body"]), tcell("NRST/RESET", styles["body"]), tcell("硬件复位，救砖/稳定连接有帮助", styles["body"]), tcell("推荐", styles["body"])],
        [tcell("TX", styles["body"]), tcell("MCU RX", styles["body"]), tcell("虚拟串口输出到目标", styles["body"]), tcell("可选", styles["body"])],
        [tcell("RX", styles["body"]), tcell("MCU TX", styles["body"]), tcell("目标日志回传到电脑", styles["body"]), tcell("可选", styles["body"])],
        [tcell("3V3/5V", styles["body"]), tcell("目标板供电口", styles["body"]), tcell("供电或从目标板取电，按板卡电源设计选择", styles["body"]), tcell("按情况", styles["body"])],
    ]
    story.append(styled_table(swd, [25 * mm, 38 * mm, 68 * mm, 29 * mm]))
    story.append(Spacer(1, 5 * mm))
    story.append(p("电源原则", styles["h2"]))
    story.append(
        bullet_list(
            [
                "有线模式：调试器插电脑，目标板仍应按自己的正常方式供电；调试器和目标板必须共地。",
                "无线模式：目标板端从机需要由目标板供电，手册支持 3.3V 和 5V，推荐使用目标板的 5V 输入口。",
                "裸 MCU 或没有 5V 转 3.3V 稳压的最小系统，只接 3V3，不要接 5V 到 VDD。",
            ],
            styles,
        )
    )
    img = image_flow(assets.get("swd_jtag"), 112, 70)
    if img:
        story.append(Spacer(1, 4 * mm))
        story.append(img)
    story.append(PageBreak())


def add_stm32_page(story, styles):
    story.append(p("3. STM32F103RCT6 使用方法", styles["h1"]))
    story.append(p("STM32F103RCT6 属于 STM32F103 高密度系列，Keil5 中需要选择对应 Device 和 Flash 下载算法。", styles["body"]))
    story.append(Spacer(1, 4 * mm))
    wiring = [
        [tcell("调试器接口", styles["body"]), tcell("STM32F103RCT6", styles["body"]), tcell("说明", styles["body"])],
        [tcell("CLK", styles["body"]), tcell("PA14 / JTCK / SWCLK", styles["body"]), tcell("SWD 时钟。", styles["body"])],
        [tcell("DIO", styles["body"]), tcell("PA13 / JTMS / SWDIO", styles["body"]), tcell("SWD 数据。", styles["body"])],
        [tcell("RST", styles["body"]), tcell("NRST", styles["body"]), tcell("推荐接，下载失败或芯片跑飞时更容易连上。", styles["body"])],
        [tcell("GND", styles["body"]), tcell("GND/VSS", styles["body"]), tcell("必须共地。", styles["body"])],
        [tcell("3V3", styles["body"]), tcell("3.3V/VDD", styles["body"]), tcell("只在需要由调试器供电或取参考电压时连接。", styles["body"])],
        [tcell("TX/RX", styles["body"]), tcell("例如 PA10/PA9 USART1", styles["body"]), tcell("可选串口：调试器 TX 接 MCU RX，调试器 RX 接 MCU TX。", styles["body"])],
    ]
    story.append(styled_table(wiring, [30 * mm, 55 * mm, 75 * mm]))
    story.append(Spacer(1, 5 * mm))
    story.append(p("Keil5 烧录配置", styles["h2"]))
    story.append(
        bullet_list(
            [
                "安装 Keil MDK 5.29 或更高版本，并在 Pack Installer 安装 STM32F1xx_DFP。",
                "Options for Target -> Device：选择 STM32F103RC 或与你工程一致的 STM32F103R 系列器件。",
                "Options for Target -> Debug：选择 CMSIS-DAP Debugger，Settings 中 Port 选择 SW；初次建议 Max Clock 设 1MHz 或 4MHz。",
                "Settings -> Flash Download：添加 STM32F10x High-density Flash。STM32F103RCT6 为 256KB Flash，不要误选 128KB Medium-density。",
                "勾选 Erase Sectors、Program、Verify；需要下载后立即运行时勾选 Reset and Run。",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p("下载失败时先按住板子的 RESET，再点 Keil 的 Load；或把 SWD Clock 降到 1MHz。", styles["note"]))
    story.append(PageBreak())


def add_mspm0_page(story, styles):
    story.append(p("4. MSPM0G3507 使用方法", styles["h1"]))
    story.append(p("MSPM0G3507 使用 ARM Cortex-M0+ 内核，烧录同样走 SWD。目标板上若有 SWD 排针，优先按排针丝印接线。", styles["body"]))
    story.append(Spacer(1, 4 * mm))
    wiring = [
        [tcell("调试器接口", styles["body"]), tcell("MSPM0G3507", styles["body"]), tcell("说明", styles["body"])],
        [tcell("CLK", styles["body"]), tcell("PA20 / SWCLK", styles["body"]), tcell("SWD 时钟。", styles["body"])],
        [tcell("DIO", styles["body"]), tcell("PA19 / SWDIO", styles["body"]), tcell("SWD 数据。", styles["body"])],
        [tcell("RST", styles["body"]), tcell("NRST", styles["body"]), tcell("推荐接，便于复位连接。", styles["body"])],
        [tcell("GND", styles["body"]), tcell("GND/VSS", styles["body"]), tcell("必须共地。", styles["body"])],
        [tcell("3V3", styles["body"]), tcell("3.3V/VDD", styles["body"]), tcell("MSPM0 是 3.3V 系统为主，裸芯片不要接 5V。", styles["body"])],
        [tcell("TX/RX", styles["body"]), tcell("按工程 UART 引脚", styles["body"]), tcell("可选串口，仍然交叉连接。", styles["body"])],
    ]
    story.append(styled_table(wiring, [30 * mm, 55 * mm, 75 * mm]))
    story.append(Spacer(1, 5 * mm))
    story.append(p("Keil5 环境", styles["h2"]))
    story.append(
        bullet_list(
            [
                "建议使用 Keil MDK 5.38a 或更新版本，Arm Compiler 6.16 或更新版本。",
                "安装 TI MSPM0 SDK 和 SysConfig；Pack Installer 中安装 TI MSPM0G1X0X_G3X0X_DFP。",
                "建议从 MSPM0 SDK 的 Keil 示例工程开始，例如 empty_driverlib，再移植自己的代码。",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p("Keil5 烧录配置", styles["h2"]))
    story.append(
        bullet_list(
            [
                "Options for Target -> Device：选择 MSPM0G3507。",
                "Debug：选择 CMSIS-DAP Debugger，Settings 中 Port 选择 SW；初次建议 Max Clock 设 1MHz。",
                "Flash Download：确认使用 MSPM0G3507 MAIN 或对应 MAIN Flash 算法。",
                "不要随意添加或擦写 NONMAIN 算法。NONMAIN 是器件配置区域，配置错误可能造成芯片锁定或难以恢复。",
            ],
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(p("如果 Keil 能识别 CMSIS-DAP，但右侧 SW Device 空白，优先检查 PA19/PA20 是否接反、目标板是否供电、NRST 是否被外围电路拉死。", styles["note"]))
    story.append(PageBreak())


def add_keil_page(story, styles, assets):
    story.append(p("5. Keil5 通用烧录流程", styles["h1"]))
    steps = [
        [tcell("步骤", styles["body"]), tcell("操作", styles["body"]), tcell("判断标准", styles["body"])],
        [tcell("1", styles["body"]), tcell("插入 PC 端调试器。无线时 PC 端应为蓝灯 Host。", styles["body"]), tcell("设备管理器出现 USB-HID 和虚拟串口。", styles["body"])],
        [tcell("2", styles["body"]), tcell("连接目标板 SWD：CLK、DIO、GND、RST。", styles["body"]), tcell("目标板正常供电，调试器与目标板共地。", styles["body"])],
        [tcell("3", styles["body"]), tcell("Keil Options for Target -> Debug -> Use: CMSIS-DAP Debugger。", styles["body"]), tcell("Settings 可进入 CMSIS-DAP 配置窗口。", styles["body"])],
        [tcell("4", styles["body"]), tcell("Settings -> Debug：Port 选 SW，降低 Max Clock 到 1MHz 初测。", styles["body"]), tcell("右侧 SW Device 能显示 ARM CoreSight SW-DP 或目标设备。", styles["body"])],
        [tcell("5", styles["body"]), tcell("Settings -> Flash Download：添加目标芯片 Flash 算法。", styles["body"]), tcell("算法容量和地址范围与目标芯片一致。", styles["body"])],
        [tcell("6", styles["body"]), tcell("点击 Keil 工具栏 Load 下载。", styles["body"]), tcell("Build Output 显示 Verify OK 或 Download verified successfully。", styles["body"])],
    ]
    story.append(styled_table(steps, [16 * mm, 82 * mm, 62 * mm]))
    img = image_flow(assets.get("keil_select"), 135, 98)
    if img:
        story.append(Spacer(1, 5 * mm))
        story.append(img)
    story.append(PageBreak())
    story.append(p("6. Flash Download 配置重点", styles["h1"]))
    story.append(
        p(
            "Keil 识别到调试器只代表 CMSIS-DAP 通了；真正能否烧录，还取决于 Flash Download 算法是否正确。不同芯片、不同容量要选择对应算法。",
            styles["body"],
        )
    )
    data = [
        [tcell("目标芯片", styles["body"]), tcell("Flash 算法重点", styles["body"])],
        [tcell("STM32F103RCT6", styles["body"]), tcell("选择 STM32F10x High-density Flash，容量 256KB。", styles["body"])],
        [tcell("MSPM0G3507", styles["body"]), tcell("选择 MSPM0G3507 MAIN 或 MSPM0 MAIN Flash，不随意操作 NONMAIN。", styles["body"])],
    ]
    story.append(styled_table(data, [42 * mm, 118 * mm]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        p(
            "注意：下方截图来自调试器手册，仅用于指示 Flash Download 配置位置；截图红框中的 Medium-density 128k 是示例，不适用于 STM32F103RCT6。STM32F103RCT6 请按上表选择 High-density 256KB。",
            styles["note"],
        )
    )
    img = image_flow(assets.get("keil_flash"), 128, 106)
    if img:
        story.append(Spacer(1, 5 * mm))
        story.append(img)
    story.append(PageBreak())


def add_troubleshooting(story, styles):
    story.append(p("7. 常见问题排查", styles["h1"]))
    problems = [
        [tcell("现象", styles["body"]), tcell("优先排查", styles["body"])],
        [tcell("Keil 找不到 CMSIS-DAP", styles["body"]), tcell("确认 PC 端接电脑 USB；Win10/11 通常免驱，Win7 安装资料包内 mbedWinSerial 驱动；换 USB 线，避免仅充电线。", styles["body"])],
        [tcell("能看到 CMSIS-DAP，但识别不到目标", styles["body"]), tcell("检查 GND 共地、CLK/DIO 是否接反、目标板是否上电、RST 是否接错；把 SWD Clock 降到 1MHz。", styles["body"])],
        [tcell("无线模式掉线或很慢", styles["body"]), tcell("确认主从 addr 一致；降低 CONF.TXT 中 rate，例如从 2M 改到 1M 或 500K；缩短距离或调整天线方向。", styles["body"])],
        [tcell("下载后程序不运行", styles["body"]), tcell("在 Debug Settings 里设置 Reset = SYSRESETREQ；Flash Download 勾选 Reset and Run；检查启动脚 BOOT0/BOOT1。", styles["body"])],
        [tcell("STM32 下载失败", styles["body"]), tcell("确认选择 High-density Flash；按住 RESET 点击 Load；检查 PA13/PA14 是否被工程改成普通 GPIO 且外部强拉。", styles["body"])],
        [tcell("MSPM0 下载失败", styles["body"]), tcell("确认 MSPM0 DFP 已安装；只用 MAIN Flash 算法；检查 PA19/PA20/NRST；必要时使用 TI 工具恢复。", styles["body"])],
    ]
    story.append(styled_table(problems, [47 * mm, 113 * mm]))
    story.append(Spacer(1, 5 * mm))
    story.append(p("上电前检查清单", styles["h2"]))
    story.append(
        bullet_list(
            [
                "目标板电源电压正确，3.3V 芯片没有被 5V 直灌。",
                "GND 已共地，SWCLK/SWDIO 没有接反。",
                "无线 PC 端是蓝灯，目标端是绿灯；有线模式是红灯。",
                "Keil 设备、Debug 适配器、Flash 算法三处都选对。",
                "首次下载先用低 SWD 频率，成功后再提高速度。",
            ],
            styles,
        )
    )
    story.append(PageBreak())


def add_sources(story, styles):
    story.append(p("8. 资料来源与版本说明", styles["h1"]))
    source_data = [
        [tcell("资料", styles["body"]), tcell("用途", styles["body"])],
        [tcell("本地：塔克 l 无线高速DAP调试下载器手册 V3.0.1", styles["body"]), tcell("调试器模式、接口定义、无线配对、Keil CMSIS-DAP 配置截图。", styles["body"])],
        [tcell("ST: STM32F103RC 官方数据手册", styles["body"]), tcell("确认 STM32F103RCT6 的 PA13/SWDIO、PA14/SWCLK、NRST 等调试相关引脚。", styles["body"])],
        [tcell("TI: MSPM0G3507 官方数据手册", styles["body"]), tcell("确认 MSPM0G3507 的 PA19/SWDIO、PA20/SWCLK、NRST 等调试相关引脚。", styles["body"])],
        [tcell("TI: MSPM0 SDK Keil QuickStart", styles["body"]), tcell("确认 MSPM0 在 Keil/MDK 下的版本、Pack 和工程使用建议。", styles["body"])],
    ]
    story.append(styled_table(source_data, [58 * mm, 102 * mm]))
    story.append(Spacer(1, 5 * mm))
    urls = [
        "ST STM32F103RC datasheet: https://www.st.com/resource/en/datasheet/stm32f103rc.pdf",
        "TI MSPM0G3507 datasheet: https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf",
        "TI MSPM0 Keil QuickStart: https://software-dl.ti.com/msp430/esd/MSPM0-SDK/latest/docs/english/quickstart_guides/doc_guide/doc_guide-srcs/quickstart_guide_keil.html",
    ]
    story.append(p("<br/>".join(urls), styles["small"]))
    story.append(Spacer(1, 6 * mm))
    story.append(p("生成说明：本指南面向比赛/实验场景，重点是让你能快速完成接线、识别调试器、在 Keil5 中烧录。若实际目标板已有标准 SWD 排针，优先按目标板排针丝印接线；若直接接芯片脚，请再次核对对应封装的官方 pinout。", styles["note"]))


def build_pdf():
    setup_fonts()
    assets = prepare_assets()
    styles = make_styles()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=16 * mm,
        title="Wireless DAP Keil5 Guide",
        author="OpenAI Codex",
    )
    story = []
    add_title_page(story, styles, assets)
    add_modes_page(story, styles, assets)
    add_wiring_common(story, styles, assets)
    add_stm32_page(story, styles)
    add_mspm0_page(story, styles)
    add_keil_page(story, styles, assets)
    add_troubleshooting(story, styles)
    add_sources(story, styles)
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUT_PDF)


if __name__ == "__main__":
    build_pdf()
