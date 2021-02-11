from subprocess import call
class SystemVolumeController():
    def __init(self):
        pass

    def set_volume(self, volume_level):
        volume = (volume_level / 100) * 65565
        call(["amixer", "sset", "Master", str(volume)])