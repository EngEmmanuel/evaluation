import json
from pathlib import Path


class ExperimentDatasetAnalyser():
    def __init__(self, results_dir:Path) -> None:
        self.results_dir = results_dir

    def _get_answer_file(self):
        pass

    def _get_results_files(self):
        self.paths = [x for x in self.results_dir.glob("via_project_*.json")]


    @staticmethod
    def _interpret_response(result, response):
        '''
        Converts the response from a number to a readable format
        '''
        return result["attribute"]["1"]["options"][response]


    def get_results(self):
        results = {}
        for p in self.paths:
            # File level
            with open(p, 'r') as f:
                result = json.load(f)

            responses = result["metadata"]
            img_level_dict = {}
            for (k,v) in responses.items():
                # Image level
                n = k[0]
                img_name = f["file"][n]

                response =  __class__._interpret_response(v["av"]["1"])

                img_level_dict[img_name] = response


            results[result["project"]["created"]] = img_level_dict