from pathlib import Path
from random import seed, sample

seed = 1


class ExperimentDatasetMaker():

    def __init__(self, real_data_path, fake_data_paths, set_name, n=10) -> None:
        self.real_data_path = real_data_path
        self.fake_data_paths = fake_data_paths
        self.set_name = set_name
        self.n = n

    def _sample_images(path: Path, n:int, ext="png"):
        '''
        Samples :n: files with extension :ext: at the location :path:
        '''
        img_fpaths = [f for f in path.glob(f"*.{ext}")]
        return sample(img_fpaths, n)

    def get_rf_images(self):
        n_real = len(self.fake_data_paths)*self.n
        r_images = self._sample_images(self.real_data_path, n=n_real)

        for p in self.fake_data_paths:
            pass

    




    '''
    true_paths =
    [
        ["img_001", "img_034"],
        ["img_342", "img_352"],
        .
        .
        ["img_313", "img_978"]
    ]
    
    rf_maps =
    [
        ["r", "f"],
        ["f", "r"],
        .
        .
        ["f", "r"]
    ]

    new_paths = 
    [
        ["pair_00, pair_01],
        ["pair_10, pair_1l1],
        .
        .

        ["pair_n0, pair_n1],
    ]

    {
        "img_001": {
            "test_set_id": "blah",
            "state": (r or f),
            "set_name": "pair_41"
        }
    }
    '''

