---
date: 2025-04-15
# description: ""
# image: ""
lastmod: 2025-04-15
showTableOfContents: false
tags:
  - PVE
  - OpenWrt
  - HomeLab
featured: true
title: "PVE 将 OpenWrt 虚拟机迁移至其他实例"
type: "post"
---

因为需要下线维护当前的 PVE 实例，所以新建了一台 PVE 实例，需要把之前的虚拟机迁移到新的 PVE 实例上，但是通过组建集群复制的方式会从当前的 PVE 中删除该实例，并且新的实例是临时性的，组建集群会带来额外的维护成本，因此通过命令行迁移

## 备份虚拟机

将虚拟机备份到 `~/workspace` 目录下

```bash
mkdir ~/workspace
```

以快照方式备份虚拟机

```bash
vzdump 122 --dumpdir ~/workspace --mode snapshot
```

```bash
INFO: starting new backup job: vzdump 122 --dumpdir /root/workspace/ --mode snapshot
INFO: Starting Backup of VM 122 (qemu)
INFO: Backup started at 2025-04-18 09:27:15
INFO: status = running
INFO: VM Name: op
INFO: include disk 'sata0' 'local-lvm:vm-122-disk-0' 20604M
INFO: backup mode: snapshot
INFO: ionice priority: 7
INFO: creating vzdump archive '/root/workspace/vzdump-qemu-122-2025_04_18-09_27_17.vma 125'
INFO: started backup task '843879b9-5054-4a96-98b2-a87994c97539'
INFO: resuming VM again
INFO: 100% (20.1 GiB of 20.1 GiB) in 2s, read: 10.1 GiB/s, write: 169.4 MiB/s
INFO: backup is sparse: 19.79 GiB (98%) total zero data
INFO: transferred 20.12 GiB in 2 seconds (10.1 GiB/s)
INFO: archive file size: 341MB
INFO: Finished Backup of VM 122 (00:00:02)
INFO: Backup finished at 2025-04-18 09:27:57
INFO: Backup job finished successfully
```

待备份完成后，会生成一个 .vma 后缀的备份文件

## 将虚拟机备份传输到目标服务器

注意不要修改文件名，因为恢复时需要使用文件名信息检查备份时间，否则可能会提示错误: `error before or during data restore, some or all disks were not completely restored. VM 124 state is NOT cleaned up.ERROR: couldn't determine archive info from xxx`

```bash
rsync -avhW --info=progress2 /root/workspace/vzdump-qemu-122-2025_04_18-09_27_17.vma 192.168.2.3:/root/workspace/
```

## 还原虚拟机

还原是指定新的虚拟机 ID，避免和现有的冲突

```bash
qmrestore ~/workspace/vzdump-qemu-122-2025_04_18-09_27_17.vma 125
```


```bash
restore vma archive: vma extract -v -r /var/tmp/vzdumptmp1083179.fifo /root/workspace/vzdump-qemu-122-2025_04_18-09_27_17.vma /var/tmp/vzdumptmp1083179
CFG: size: 468 name: qemu-server.conf
DEV: dev_id=1 size: 21604859904 devname: drive-sata0
CTIME: Fri Apr 18 09:27:17 2025
  WARNING: You have not turned on protection against thin pools running out of space.
  WARNING: Set activation/thin_pool_autoextend_threshold below 100 to trigger automatic extension of thin pools before they get full.
  Logical volume "vm-125-disk-0" created.
  WARNING: Sum of all thin volume sizes (520.36 GiB) exceeds the size of thin pool pve/data and the size of whole volume group (<475.94 GiB).
new volume ID is 'local-lvm:vm-125-disk-0'
map 'drive-sata0' to '/dev/pve/vm-125-disk-0' (write zeros = 0)
progress 1% (read 216072192 bytes, duration 0 sec)
progress 2% (read 432144384 bytes, duration 0 sec)
progress 3% (read 648151040 bytes, duration 0 sec)
progress 4% (read 864223232 bytes, duration 0 sec)
progress 5% (read 1080295424 bytes, duration 0 sec)
progress 6% (read 1296302080 bytes, duration 0 sec)
progress 7% (read 1512374272 bytes, duration 0 sec)
progress 8% (read 1728446464 bytes, duration 0 sec)
progress 9% (read 1944453120 bytes, duration 0 sec)
progress 10% (read 2160525312 bytes, duration 0 sec)
progress 11% (read 2376597504 bytes, duration 0 sec)
progress 12% (read 2592604160 bytes, duration 0 sec)
progress 13% (read 2808676352 bytes, duration 0 sec)
progress 14% (read 3024683008 bytes, duration 0 sec)
progress 15% (read 3240755200 bytes, duration 0 sec)
progress 16% (read 3456827392 bytes, duration 0 sec)
progress 17% (read 3672834048 bytes, duration 0 sec)
progress 18% (read 3888906240 bytes, duration 0 sec)
progress 19% (read 4104978432 bytes, duration 0 sec)
progress 20% (read 4320985088 bytes, duration 0 sec)
progress 21% (read 4537057280 bytes, duration 0 sec)
progress 22% (read 4753129472 bytes, duration 0 sec)
progress 23% (read 4969136128 bytes, duration 0 sec)
progress 24% (read 5185208320 bytes, duration 0 sec)
progress 25% (read 5401214976 bytes, duration 0 sec)
progress 26% (read 5617287168 bytes, duration 0 sec)
progress 27% (read 5833359360 bytes, duration 0 sec)
progress 28% (read 6049366016 bytes, duration 0 sec)
progress 29% (read 6265438208 bytes, duration 0 sec)
progress 30% (read 6481510400 bytes, duration 0 sec)
progress 31% (read 6697517056 bytes, duration 0 sec)
progress 32% (read 6913589248 bytes, duration 0 sec)
progress 33% (read 7129661440 bytes, duration 0 sec)
progress 34% (read 7345668096 bytes, duration 0 sec)
progress 35% (read 7561740288 bytes, duration 0 sec)
progress 36% (read 7777812480 bytes, duration 0 sec)
progress 37% (read 7993819136 bytes, duration 0 sec)
progress 38% (read 8209891328 bytes, duration 0 sec)
progress 39% (read 8425897984 bytes, duration 0 sec)
progress 40% (read 8641970176 bytes, duration 0 sec)
progress 41% (read 8858042368 bytes, duration 0 sec)
progress 42% (read 9074049024 bytes, duration 0 sec)
progress 43% (read 9290121216 bytes, duration 0 sec)
progress 44% (read 9506193408 bytes, duration 0 sec)
progress 45% (read 9722200064 bytes, duration 0 sec)
progress 46% (read 9938272256 bytes, duration 0 sec)
progress 47% (read 10154344448 bytes, duration 0 sec)
progress 48% (read 10370351104 bytes, duration 0 sec)
progress 49% (read 10586423296 bytes, duration 0 sec)
progress 50% (read 10802429952 bytes, duration 0 sec)
progress 51% (read 11018502144 bytes, duration 0 sec)
progress 52% (read 11234574336 bytes, duration 0 sec)
progress 53% (read 11450580992 bytes, duration 0 sec)
progress 54% (read 11666653184 bytes, duration 0 sec)
progress 55% (read 11882725376 bytes, duration 0 sec)
progress 56% (read 12098732032 bytes, duration 0 sec)
progress 57% (read 12314804224 bytes, duration 0 sec)
progress 58% (read 12530876416 bytes, duration 0 sec)
progress 59% (read 12746883072 bytes, duration 0 sec)
progress 60% (read 12962955264 bytes, duration 0 sec)
progress 61% (read 13179027456 bytes, duration 0 sec)
progress 62% (read 13395034112 bytes, duration 0 sec)
progress 63% (read 13611106304 bytes, duration 0 sec)
progress 64% (read 13827112960 bytes, duration 0 sec)
progress 65% (read 14043185152 bytes, duration 0 sec)
progress 66% (read 14259257344 bytes, duration 0 sec)
progress 67% (read 14475264000 bytes, duration 0 sec)
progress 68% (read 14691336192 bytes, duration 0 sec)
progress 69% (read 14907408384 bytes, duration 0 sec)
progress 70% (read 15123415040 bytes, duration 1 sec)
progress 71% (read 15339487232 bytes, duration 1 sec)
progress 72% (read 15555559424 bytes, duration 1 sec)
progress 73% (read 15771566080 bytes, duration 1 sec)
progress 74% (read 15987638272 bytes, duration 1 sec)
progress 75% (read 16203644928 bytes, duration 1 sec)
progress 76% (read 16419717120 bytes, duration 1 sec)
progress 77% (read 16635789312 bytes, duration 1 sec)
progress 78% (read 16851795968 bytes, duration 1 sec)
progress 79% (read 17067868160 bytes, duration 1 sec)
progress 80% (read 17283940352 bytes, duration 1 sec)
progress 81% (read 17499947008 bytes, duration 1 sec)
progress 82% (read 17716019200 bytes, duration 1 sec)
progress 83% (read 17932091392 bytes, duration 1 sec)
progress 84% (read 18148098048 bytes, duration 1 sec)
progress 85% (read 18364170240 bytes, duration 1 sec)
progress 86% (read 18580242432 bytes, duration 1 sec)
progress 87% (read 18796249088 bytes, duration 1 sec)
progress 88% (read 19012321280 bytes, duration 1 sec)
progress 89% (read 19228327936 bytes, duration 1 sec)
progress 90% (read 19444400128 bytes, duration 1 sec)
progress 91% (read 19660472320 bytes, duration 1 sec)
progress 92% (read 19876478976 bytes, duration 1 sec)
progress 93% (read 20092551168 bytes, duration 1 sec)
progress 94% (read 20308623360 bytes, duration 1 sec)
progress 95% (read 20524630016 bytes, duration 1 sec)
progress 96% (read 20740702208 bytes, duration 1 sec)
progress 97% (read 20956774400 bytes, duration 1 sec)
progress 98% (read 21172781056 bytes, duration 1 sec)
progress 99% (read 21388853248 bytes, duration 1 sec)
progress 100% (read 21604859904 bytes, duration 1 sec)
total bytes read 21604859904, sparse bytes 21249482752 (98.4%)
space reduction due to 4K zero blocks 0.818%
rescan volumes...
```

还原结束后修改 IP、MAC 等信息，即可启动虚拟机，完成迁移