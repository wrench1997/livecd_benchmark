import os
import subprocess
import tempfile
from distutils.version import LooseVersion
import re

# 定义变量
OUTPUT_ISO = "my_livecd.iso"
WORK_DIR = tempfile.mkdtemp()
KERNEL_PACKAGE = "linux-image-generic"  # 需要替换为实际可用的内核包名
INITRD_IMAGE_PATTERN = "/boot/initrd.img-{}"  # 根据实际情况获取当前内核的initrd
ISOLINUX_CFG = "isolinux/isolinux.cfg"  # 引导加载器配置文件
SYSTEM_MAP_PATTERN = "/boot/System.map-{}"  # 内核符号表（如果需要）

# 准备工作目录
os.makedirs(f"{WORK_DIR}/iso", exist_ok=True)
os.makedirs(f"{WORK_DIR}/rootfs", exist_ok=True)

# 获取内核和initrd
subprocess.run(["apt-get", "download", KERNEL_PACKAGE], capture_output=True)
subprocess.run(["dpkg-deb", "-x", "*.deb", f"{WORK_DIR}/rootfs"])

# 获取当前内核版本
current_kernel_version = subprocess.check_output(["uname", "-r"]).decode().strip()
initrd_image = INITRD_IMAGE_PATTERN.format(current_kernel_version)
system_map = SYSTEM_MAP_PATTERN.format(current_kernel_version)

# 拷贝initrd到rootfs
subprocess.run(["cp", initrd_image, f"{WORK_DIR}/rootfs"])

# 制作精简版rootfs，仅包含基本系统文件
rsync_command = ["rsync", "-aHAXSP", "--exclude={/dev/*,/proc/*,/sys/*,/tmp/*,/run/*,/mnt/*,/media/*,/lost+found,/home/*}", "/", f"{WORK_DIR}/rootfs/"]
subprocess.run(rsync_command)

# 处理引导加载器配置
subprocess.run(["cp", "/usr/lib/syslinux/isolinux.bin", f"{WORK_DIR}/isolinux/"])
subprocess.run(["cp", "/usr/share/syslinux/isolinux.cfg", f"{WORK_DIR}/{ISOLINUX_CFG}"])
# 对isolinux.cfg进行修改以指向新的内核和initrd，这里假设您已经实现了这个功能，因为它涉及到文件内容的修改

# 创建ISO镜像
mkisofs_command = [
    "mkisofs",
    "-r", "-J", "-b", "isolinux/isolinux.bin",
    "-c", "isolinux/boot.cat", "-no-emul-boot",
    "-boot-load-size", "4", "-boot-info-table",
    "-input-charset", "utf-8", "-quiet", "-V", "MyLiveCD",
    "-o", OUTPUT_ISO,
    f"{WORK_DIR}/rootfs"
]
subprocess.run(mkisofs_command)

# 清理临时文件
subprocess.run(["rm", "-rf", WORK_DIR])

print(f"ISO image created at {OUTPUT_ISO}")