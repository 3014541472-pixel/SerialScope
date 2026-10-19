# SerialScope

STM32F103C8T6 + Python 实时数据监控项目。包含可切换的模拟/串口 GUI、文本协议、CSV 导出，以及独立的 STM32 裸机固件。

**验证边界：** Python 协议和虚拟串口测试可在无开发板条件下运行。STM32 固件提供 demo 与 ADC 两种构建配置；真实烧录、接线和测量仍需在开发板上验收。仓库中的历史 CSV/TXT 文件不是本版本的硬件验证证据。

## 系统结构

传感器/电位器 → PA0 / ADC1 → STM32F103C8T6 → USART1 → USB-to-TTL → Python GUI → CSV / TXT

无开发板时，点击 **Simulate** 即可展示生成波形。模拟数据与串口数据在界面、日志、CSV 的 source 列中分别标记。

## Windows 启动

安装 Python（需含 Tkinter），在项目文件夹终端运行：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

1. 点击 Simulate 测试界面。
2. 接入 USB-to-TTL 后点击 Refresh，选择实际 COM 端口（不固定为 COM5）。
3. 选择 115200，点击 Connect。串口参数为 8 数据位、无校验、1 停止位（8N1）。
4. Export CSV 保存最近最多 100000 条有效样本，Save Log 保存最近 2000 条日志；超出上限覆盖最旧记录。请及时导出。
5. 断线后检查接线和端口，再点击 Connect。Clear 清空显示、计数及待导出记录。

GUI 每 50 ms 非阻塞轮询串口，每次最多读 4096 字节。当前适用于低速教学采样，不保证高吞吐连续存盘。发送框发送以 LF 结尾的文本；附带固件仅发送数据，不处理电脑命令。

## 协议

```text
DEVICE_DATA,ID=1,VALUE=1.650\r\n
```

每帧以 LF 换行结束，可带 CR；最长 256 字节。ID 表示样本序号（为兼容旧代码，解析结果字段仍叫 sensor_id），VALUE 为有限数值。附带固件输出单位为 V。错误字段、非有限数值和超长帧不会进入曲线；超长帧丢弃至下一个换行。

## STM32 固件构建

采用寄存器方式，避免依赖未安装的 HAL 包。复位后使用内部 HSI 8 MHz；无需外部晶振。需要 ARM GNU Toolchain、CMake 3.20+ 和 Ninja，并保证命令位于 PATH。

```powershell
arm-none-eabi-gcc --version
cmake -S firmware -B build/demo -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/arm-gcc.cmake -DDEMO_MODE=ON
cmake --build build/demo
```

生成 build/demo/serialscope.elf、serialscope.bin、serialscope.map。默认 demo 在 STM32 内生成递增斜坡，验证串口链路，不代表 ADC 测量。

ADC 版本采样 PA0，按约 100 ms 间隔发送（非精确定时采样）：

```powershell
cmake -S firmware -B build/adc -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/arm-gcc.cmake -DDEMO_MODE=OFF -DVREF_MV=3300
cmake --build build/adc
```

换算：电压 = ADC 原始码 × VREF_MV / 4095 / 1000。VREF_MV 默认 3300 mV，请依据实测参考电压修正；内部 HSI 和参考电压误差会影响通信与测量精度。此版本不是精密示波器。

## 接线和烧录

先确认板卡标识、USB-to-TTL 的信号电平与跳帽含义。**UART 逻辑信号使用 3.3 V；不要因模块存在 3V3 电源引脚就假定 TXD 电平一定是 3.3 V。** 开发板可通过其 USB 单独供电，TTL 模块电源脚不接，双方共地。

| STM32 引脚 | USB-to-TTL 引脚 | 说明 |
|---|---|---|
| PA9 / USART1 Transmit Data（发送数据） | RXD / Receive Data（接收数据） | 固件输出到电脑 |
| PA10 / USART1 Receive Data（接收数据） | TXD / Transmit Data（发送数据） | ROM 串口烧录时需要；当前应用不接收命令 |
| GND / Ground（地） | GND / Ground（地） | 必须共地 |
| PA0 / Port A Pin 0（A 端口第 0 引脚） | 不接 TTL 模块 | ADC 模拟输入 |

UART ROM 烧录：确认实际芯片支持 USART1 系统 Bootloader，断电设置 BOOT0（Boot configuration 0，启动配置位 0）为 1、BOOT1（Boot configuration 1，启动配置位 1）为 0，然后复位。在 STM32CubeProgrammer 选择 UART 和实际 COM 端口，连接后将 .bin 下载到 **0x08000000**。完成后将 BOOT0 改回 0 并复位运行。烧录时先关闭 GUI 串口连接；运行 GUI 前断开 CubeProgrammer，避免端口占用。

ADC 初测：PA0 接 Ground 时应接近 0 V；也可用电位器两端连接板上 3.3 V 与 Ground，滑动端接 PA0。PA0 电压必须处于 Ground 到板上 VDDA（Analog Supply Voltage，模拟电源电压）范围内，通常约 0–3.3 V；不要输入 5 V，不要悬空进行准确性判断。

参考：[ST RM0008](https://www.st.com/resource/en/reference_manual/cd00171190-stm32f101-103-105-107-stm32f100-series-armbased-32bit-mcus-stmicroelectronics.pdf)、[ST AN2606 系统存储器启动模式](https://www.st.com/resource/en/application_note/cd00167594-stm32-microcontroller-system-memory-boot-mode-stmicroelectronics.pdf)。具体开发板跳帽位置需看实物。

## 测试与验收

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_protocol.py -v
```

自动测试覆盖有效/错误帧、半帧、多帧、超长帧恢复、断开及重连缓冲清理，使用 PySerial loop://，无需硬件。旧 tests/test_parser.py 等脚本保留作历史学习记录。GitHub Actions 运行 Python 检查和两种固件构建，并上传构建产物；以实际运行结果为准。

硬件验收顺序：demo 固件烧录 → 串口收到完整帧 → GUI 显示 → 拔插后重连 → CSV 与接收值比对 → ADC 固件接 Ground/已知电压验证。未实测前不勾选硬件验收任务。

进度：[Issue #1](https://github.com/3014541472-pixel/SerialScope/issues/1)。
