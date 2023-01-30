from human_test.helper_funcs.generate_json_parts import *

if __name__ == "__main__":
    base_path = Path(r"C:\Users\spet4299\Documents\DPhil\Research\TEE_Generation")
    p = base_path / "evaluation\human_test\helper_funcs\json_parts"
    fname = "test"
    n_images = 12
    gen_file_part(base_path/f"{fname}_file.json", n_images=n_images)
    gen_view_part(base_path/f"{fname}_view.json", n_images=n_images)