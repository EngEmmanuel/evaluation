import json
import copy
from pathlib import Path


class ExperimentDatasetAnalyser():
    def __init__(self, results_dir: Path, answer_file: Path) -> None:
        self.results_dir = results_dir
        self.answer_file = answer_file
        self.paths = None
        self.answers = None
        self.dir_responses = None
        self.images_per_dir = None

        self._get_results_files()

    def _get_answer_json(self):
        with open(self.answer_file, "r") as f:
            self.answers = json.load(f)

    def _get_results_files(self):
        self.paths = [x for x in self.results_dir.glob("via_project_*.json")]

    @staticmethod
    def _interpret_response(result, response):
        '''
        Converts the response from a number to a readable format
        '''
        return result["attribute"]["1"]["options"][response]

    def _get_responses(self):
        '''
        For all response JSON files, this function reads the JSON and stores the participant response in a dict
        '''
        dir_responses = {}
        for p in self.paths:
            # File level
            with open(p, 'r') as f:
                file_results = json.load(f)

            file_responses = file_results["metadata"]
            img_level_dict = {}
            for (meta_id, response_dict) in file_responses.items():
                # Image level
                n = meta_id[0]
                img_name = file_results["file"][n]["src"]

                response = __class__._interpret_response(
                    result=file_results, response=response_dict["av"]["1"])

                img_level_dict[img_name] = response

            dir_responses[file_results["project"]["created"]] = img_level_dict

        print(*dir_responses.items(), sep='\n')
        self.dir_responses = dir_responses

    @staticmethod
    def _calc_score(answers, responses):
        # responses = {"img_n: resp, ..., "}
        score = {
            "score": 0,
            "Real": 0,
            "Synthetic": 0
        }
        score = {
            "score": 0,
            "RealReal": 0,
            "SyntheticSynthetic": 0,
            "RealSynthetic": 0,
            "SyntheticReal": 0
        }
        for (k, v) in responses.items():
            answer = answers[k]['state']
            mark = int(answer == v)

            score[answer+v] += 1
            if mark:
                score["score"] += 1

        return score

    def calculate_results(self):
        self._get_answer_json()
        self._get_responses()

        # Results across people

        def calculate_per_person():
            person_dict = {}
            for (k, v) in self.dir_responses.items():
                person_dict[k] = __class__._calc_score(self.answers, v)

            print("NEW", *person_dict.items(), "ENDpd\n", sep='\n')

        # Results acrosss files from different src folders. Shows whic

        def calculate_per_data_src():
            data_src_template = {
                i: 0 for i in self.answers["metadata"]["src_dirs"]}
            data_src = copy.deepcopy(data_src_template)
            data_src_per_person = {}

            for (person_id, img_responses) in self.dir_responses.items():
                data_src_per_person[person_id] = copy.deepcopy(
                    data_src_template)
                for (img_n, response) in img_responses.items():
                    answer = self.answers[img_n]['state']
                    img_src = self.answers[img_n]["src_dir"]

                    data_src[img_src] += int(answer == response)
                    data_src_per_person[person_id][img_src] += int(
                        answer == response)

            print(*data_src.items(), "END\n", sep='\n')
            print(*data_src_per_person.items(), "END\n", sep='\n')

            total_real = self.images_per_dir/2
            total_fake = total_real
            n_fake_per_gen = self.images_per_dir/(len(self.answers["metadata"]["src_dirs"]) + 1 )


            for (k,v) in data_src.items():
                if k == "real":
                    pct = 100*(v/total_real)
                else:
                    pct = 100*(v/n_fake_per_gen)
                print("{pct} of {src_dir} images were correctly labelled".format(pct=pct, src_dir=k))

        calculate_per_person()
        calculate_per_data_src()

        # Results for certain images??? i.e. which ones were really believable etc.????
