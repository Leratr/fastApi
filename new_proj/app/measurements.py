import psutil

CPU_COUNT = psutil.cpu_count()

cpu = [[None]*100 for _ in range(CPU_COUNT)]

def update_msts():
    _cpu = psutil.cpu_percent(percpu=True)

    for i in range(CPU_COUNT):
        cpu[i][:-1] = cpu[i][1:]
        cpu[i][-1] = _cpu[i]
