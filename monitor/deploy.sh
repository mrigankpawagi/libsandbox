#!/usr/bin/bash
# Compile and "deploy" a new custom kernel from source on Arch Linux

# Change this if you'd like. It has no relation
# to the suffix set in the kernel config.
SUFFIX="-libsandbox"

# This causes the script to exit if an error occurs
set -e

# Compile the kernel
make -j$(nproc)
# Compile and install modules
make -j$(nproc) modules_install

# Install kernel image
cp arch/x86_64/boot/bzImage /boot/vmlinuz-linux$SUFFIX

# Create preset and build initramfs
sed s/linux/linux$SUFFIX/g \
    </etc/mkinitcpio.d/linux.preset \
    >/etc/mkinitcpio.d/linux$SUFFIX.preset
mkinitcpio -p linux$SUFFIX

# Update bootloader entries with new kernels.
grub-mkconfig -o /boot/grub/grub.cfg
