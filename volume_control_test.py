from subprocess import call

volume = (50 / 100) * 65565

call(["amixer", "sset", "Master", str(volume)])