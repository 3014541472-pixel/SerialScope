# 验证记录（2026-10-20）

针对提交 50fda915be8094c41ff309ecf190a65f637e0122：

## 已执行
- Python 3.12：`python -m unittest discover -s tests -p test_protocol.py -v`，3 项测试全部通过。
- `python -m compileall -q main.py serial_manager.py data_parser.py` 通过。
- STM32 demo 和 ADC 两个配置均使用 Zig 0.13.0 内含 Clang 成功交叉编译、链接为 ARM ELF（Thumb / Cortex-M3），启用 -Wall -Wextra -Werror。
- readelf 核对向量表位于 0x08000000，ADC 版本入口为 Flash 内的 Thumb 地址，ARM EABI5。

补充交叉编译命令（在项目根目录，先创建输出目录）：

```sh
python -m ziglang cc -target thumb-freestanding-eabi -mcpu=cortex_m3 -Os -ffreestanding -fno-stack-protector -nostdlib -Wall -Wextra -Werror -DDEMO_MODE=1 -Wl,-T,firmware/stm32f103c8.ld -Wl,-e,Reset_Handler firmware/src/main.c firmware/src/startup.c -o build/clang-demo/serialscope.elf
```

ADC 配置将 DEMO_MODE 改为 0，输出目录改为 build/clang-adc。以上用于补充编译验证，不代替 README 中的 ARM GNU Toolchain/CMake 构建。

## 尚未验证
- 本地环境未安装成功 ARM GNU Toolchain，因此尚未实际执行 README 的 GCC/CMake 构建及 BIN 生成。
- GitHub Actions 首次检查已触发，记录时 Python、demo、ADC 三个任务均在排队：[运行记录](https://github.com/3014541472-pixel/SerialScope/actions/runs/39284214135)。
- 本环境无图形显示服务，未启动 Tkinter 窗口做视觉检查。
- 未连接开发板；ROM 烧录、UART 实测、ADC 电压准确性、设备拔插恢复和真实数据 CSV 比对均待用户电脑验收。
- 未录制真实硬件演示视频，未据此勾选 Issue #1 的硬件验收任务。

提供代码、通过交叉编译与通过硬件验收是不同的进度状态，请按实际实验结果更新。
