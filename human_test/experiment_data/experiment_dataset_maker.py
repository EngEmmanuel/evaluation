import json
from os import mkdir
from shutil import move, copy2
from pathlib import Path
from collections import OrderedDict
from itertools import tee
from random import seed, sample, shuffle

seed(1)


class ExperimentDatasetMaker():

    def __init__(self, real_data_path, fake_data_paths, set_name, n=10) -> None:
        '''
        :n: the number of files to be sampled from each synthetic data dir
        '''
        self.n = n
        self.set_name = set_name
        self.real_data_path, self.fake_data_paths = real_data_path, fake_data_paths
        self.r_image_paths, self.f_image_paths = [], []

        self.IMAGE_EXT = ["png", "jpg", "jpeg"]

    @staticmethod
    def _sample_images(path: Path, n: int, exts=["jpg"]):
        '''
        Samples :n: image files at the location :path:
        '''
        img_fpaths = [x for ext in exts for x in path.glob(f"*.{ext}")]
        return sample(img_fpaths, n)

    def _make_initial_dataset_dict(self):
        '''
        Creates the skeleton dictionary that will be used to store the orginal filenames
        and there new ids once anonymised alongside other information
        '''
        assert len(self.r_image_paths) == len(self.f_image_paths)
        self.dataset_dict = OrderedDict()

        for (r_p, f_p) in zip(self.r_image_paths, self.f_image_paths):
            r_key = '/'.join(r_p.parts[-2:])
            f_key = '/'.join(f_p.parts[-2:])

            self.dataset_dict[r_key] = {
                'state': 'r',
                'src_path': str(r_p),
            }
            self.dataset_dict[f_key] = {
                'state': 'f',
                'src_path': str(f_p),
            }

        return

    def _dict_to_json(self, save_path):
        '''
        Save dictionary as JSON file
        '''
        with open(save_path, "w") as outfile:
            json.dump(self.dataset_dict, outfile)

    def _copy_and_rename(old_path, new_path):
        copy2(old_path, new_path)

    def _get_rf_image_paths(self):
        '''
        Function that samples image paths from the real and fake image directories
        '''
        n_real = len(self.fake_data_paths)*self.n
        self.r_image_paths = __class__._sample_images(
            path=self.real_data_path, n=n_real, exts=self.IMAGE_EXT)

        for p in self.fake_data_paths:
            self.f_image_paths += self._sample_images(
                p, self.n, exts=self.IMAGE_EXT)
        # Shuffle f paths as currently in order of directory it was acquired from
        self.f_image_paths = sample(
            self.f_image_paths, len(self.f_image_paths))

        assert len(self.r_image_paths) == len(self.f_image_paths)

        # self.r_image_paths = [Path(f"r_img_{i}") for i in range(20)]
        # self.f_image_paths = [Path(f"f_img_{i}") for i in range(20)]

    def create_single_experiment_set(self, dest_dir: Path, ext="png"):
        self._get_rf_image_paths()
        self._make_initial_dataset_dict()

        dataset_dir = dest_dir / self.set_name / "dataset"
        metadata_dir = dest_dir / self.set_name / "metadata"
        dataset_dir.mkdir(parents=True)
        metadata_dir.mkdir(parents=True)

        items = list(self.dataset_dict.items())
        shuffle(items)
        for i, (k, v) in enumerate(items):
            a = 5
            new_img_name = f"img_{i}.{ext}"
            new_path = dataset_dir / new_img_name

            __class__._copy_and_rename(
                old_path=v["src_path"], new_path=new_path)

            self.dataset_dict[k]["set_path"] = str(new_path)
            self.dataset_dict[k]["new_name"] = new_img_name

        # Add metadata key to the info file
        self.dataset_dict["metadata"] = {
            "set_id": self.set_name,
            "n_images": i + 1
        }
        self._dict_to_json(save_path= metadata_dir/f"{self.set_name}.json")

    def create_paired_experiment_set(self, dest_dir: Path, ext="jpg"):
        '''
        Creates the dataset required for comparing real and fake images in pairs
        '''

        # pairwise() from Itertools Recipes
        def _pairwise(iterable):
            "s -> (s0,s1), (s1,s2), (s2, s3), ..."
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        l_or_r = [sample(['r', 'f'], 2)
                  for _ in range(self.n*len(self.fake_data_paths))]

        mkdir(dest_dir / self.set_name)

        for i, (k_r, v_r), (k_f, v_f) in enumerate(self._pairwise(self.dataset_dict.items())):
            '''
            Development paused. One image at a time is currently in favour.
            #TODO make it such that it skips every other step so that you are effectively
            looping in chunks of two
            '''
            _l = l_or_r[i][0]  # Decides if the real or fake image will be on the left or right
            if _l == 'f':
                r_name, f_name = f"pair_{i}{1}.{ext}", f"pair_{i}{0}.{ext}"
            else:
                r_name, f_name = f"pair_{i}{0}.{ext}", f"pair_{i}{1}.{ext}"

            r_new_path = dest_dir / self.set_name / r_name
            f_new_path = dest_dir / self.set_name / f_name

            self._copy_and_rename(v_r["src_path"], r_new_path)
            self._copy_and_rename(v_f["src_path"], f_new_path)

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
        "s1/img_001": {
            "test_set_id": "blah",
            "state": f,
            "set_name": "pair_41"
        },
        "real/img_001": {
            "test_set_id": "blah",
            "state": r,
            "set_name": "pair_30"
        },
    }
    '''
