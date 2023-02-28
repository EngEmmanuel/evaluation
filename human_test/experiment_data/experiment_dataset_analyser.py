import json
import copy
from pathlib import Path


class ExperimentDatasetAnalyser():
    '''
    Analyses the results from the real and fake quiz

    :answer_file: is the file that contains the mapping of the anonymised images to their real
    names, states and paths
    '''
    def __init__(self, results_dir: Path, answer_file: Path, imgs_per_dir) -> None:
        self.results_dir = results_dir
        self.answer_file = answer_file
        self.paths = None
        self.answers = None
        self.dir_responses = None
        self.imgs_per_dir = imgs_per_dir

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
        For all response JSON files, this function reads the JSON and stores the participant response in a dict.
        In the case where a response is missing, this info is added to missing_response:dict and the results are still calculated without
        it.
        '''
        def _make_unique_person_key(file_results):
            a = list(file_results["metadata"].keys())
            a.sort()
            return a[0]

        dir_responses = {}
        missing_response = {}
        for p in self.paths:
            # File level
            with open(p, 'r') as f:
                file_results = json.load(f)

            file_responses = file_results["metadata"]
            img_level_dict = {}
            for (meta_id, response_dict) in file_responses.items():
                # Image level
                n = meta_id.split("_")[0]
                img_name = file_results["file"][n]["src"]
                
                # Deal with missing responses
                if not response_dict["av"]:
                    if p.name in missing_response:
                        missing_response[p.name] += 1
                    else:
                        missing_response[p.name] = 1
                    continue
                # map numbers to readable responses
                response = __class__._interpret_response(
                    result=file_results, response=response_dict["av"]["1"])

                img_level_dict[img_name] = response

            dir_responses[_make_unique_person_key(file_results)] = img_level_dict
        print("\nMissing Ressponses: ", missing_response)

        #print(*dir_responses.items(), sep='\n')
        self.dir_responses = dir_responses

    @staticmethod
    def _calc_score(answers, responses):
        # responses = {"img_n: resp, ..., "}
        score = {
            "score": 0,
            "RealReal": 0,
            "SyntheticSynthetic": 0,
            "RealSynthetic": 0,
            "SyntheticReal": 0
        }
        # participants are given a mark for correct labelling
        for (k, v) in responses.items():
            answer = answers[k]['state']
            mark = int(answer == v)

            score[answer+v] += 1
            if mark:
                score["score"] += 1

        return score

    def calculate_results(self):
        print("\nNew run\n")
        self._get_answer_json()
        self._get_responses()

        # Results across people

        def calculate_per_person():
            person_dict = {}
            for (k, v) in self.dir_responses.items():
                person_dict[k] = __class__._calc_score(self.answers, v)

            print("\nParticipant Confusion matrices", *person_dict.items(), sep='\n')

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

            print("\nWhole directory Score stratified by data source: ", *data_src.items(), sep='\n')
            print("\nPer Person score stratified by data source:", *data_src_per_person.items(), sep='\n')

            total_real = (len(self.answers["metadata"]["src_dirs"]) - 1) * self.imgs_per_dir


            print("\nWhole directory summary statistics:")
            for (k,v) in data_src.items():
                if ("S" not in k):
                    pct = 100*(v/(total_real*len(self.paths)))
                else:
                    pct = 100*(v/(self.imgs_per_dir*len(self.paths)))
                print("{pct:.1f}% of {src_dir} images were correctly labelled".format(pct=pct, src_dir=k))

        calculate_per_person()
        calculate_per_data_src()

        # Results for certain images??? i.e. which ones were really believable etc.????
