#!bin/sh
cp qemu-usermode.spec qemu-usermode-static.spec
sed -i "s|^Name:.*qemu-usermode$|Name: qemu-usermode-static|g" qemu-usermode-static.spec
