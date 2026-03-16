import os
from huggingface_hub import hf_hub_download, snapshot_download

def download_musetalk_models():
    base_dir = "models"
    os.makedirs(base_dir, exist_ok=True)
    
    # MuseTalk main weights
    musetalk_pth = os.path.join(base_dir, "musetalkV15", "unet.pth")
    musetalk_json = os.path.join(base_dir, "musetalkV15", "musetalk.json")
    
    if not os.path.exists(musetalk_pth) or not os.path.exists(musetalk_json):
        print("--- Downloading MuseTalk main weights ---")
        os.makedirs(os.path.join(base_dir, "musetalkV15"), exist_ok=True)
        hf_hub_download(
            repo_id="afrizalha/musetalk-models",
            filename="musetalk/pytorch_model.bin",
            local_dir=os.path.join(base_dir, "musetalkV15")
        )
        hf_hub_download(
            repo_id="afrizalha/musetalk-models",
            filename="musetalk/musetalk.json",
            local_dir=os.path.join(base_dir, "musetalkV15")
        )
        src_bin = os.path.join(base_dir, "musetalkV15", "musetalk", "pytorch_model.bin")
        src_json = os.path.join(base_dir, "musetalkV15", "musetalk", "musetalk.json")
        if os.path.exists(src_bin):
            os.rename(src_bin, musetalk_pth)
        if os.path.exists(src_json):
            os.rename(src_json, musetalk_json)
        # cleanup
        if os.path.exists(os.path.join(base_dir, "musetalkV15", "musetalk")):
            os.rmdir(os.path.join(base_dir, "musetalkV15", "musetalk"))
    else:
        print("MuseTalk weights already exist.")

    # DWPose weights
    dwpose_pth = os.path.join(base_dir, "dwpose", "dw-ll_ucoco_384.pth")
    if not os.path.exists(dwpose_pth):
        print("--- Downloading DWPose weights ---")
        hf_hub_download(
            repo_id="afrizalha/musetalk-models",
            filename="dwpose/dw-ll_ucoco_384.pth",
            local_dir=os.path.join(base_dir, "dwpose")
        )
        src_dw = os.path.join(base_dir, "dwpose", "dwpose", "dw-ll_ucoco_384.pth")
        if os.path.exists(src_dw):
            os.rename(src_dw, dwpose_pth)
            os.rmdir(os.path.join(base_dir, "dwpose", "dwpose"))
    else:
        print("DWPose weights already exist.")
    
    # Face-Parsing weights
    fp_resnet = os.path.join(base_dir, "face-parse-bisent", "resnet18-5c106cde.pth")
    fp_iter = os.path.join(base_dir, "face-parse-bisent", "79999_iter.pth")
    if not os.path.exists(fp_resnet) or not os.path.exists(fp_iter):
        print("--- Downloading Face-Parsing weights ---")
        hf_hub_download(
            repo_id="afrizalha/musetalk-models",
            filename="face-parse-bisent/resnet18-5c106cde.pth",
            local_dir=os.path.join(base_dir, "face-parse-bisent")
        )
        hf_hub_download(
            repo_id="afrizalha/musetalk-models",
            filename="face-parse-bisent/79999_iter.pth",
            local_dir=os.path.join(base_dir, "face-parse-bisent")
        )
        for f in ["resnet18-5c106cde.pth", "79999_iter.pth"]:
            src_fp = os.path.join(base_dir, "face-parse-bisent", "face-parse-bisent", f)
            dst_fp = os.path.join(base_dir, "face-parse-bisent", f)
            if os.path.exists(src_fp):
                os.rename(src_fp, dst_fp)
        if os.path.exists(os.path.join(base_dir, "face-parse-bisent", "face-parse-bisent")):
            os.rmdir(os.path.join(base_dir, "face-parse-bisent", "face-parse-bisent"))
    else:
        print("Face-Parsing weights already exist.")

    # VAE weights
    vae_dir = os.path.join(base_dir, "sd-vae")
    if not os.path.exists(os.path.join(vae_dir, "config.json")):
        print("--- Downloading SD-VAE-FT-MSE ---")
        snapshot_download(
            repo_id="stabilityai/sd-vae-ft-mse",
            local_dir=vae_dir
        )
    else:
        print("VAE models already exist.")

    # Whisper weights
    whisper_dir = os.path.join(base_dir, "whisper")
    if not os.path.exists(os.path.join(whisper_dir, "config.json")):
        print("--- Downloading Whisper Tiny ---")
        snapshot_download(
            repo_id="openai/whisper-tiny",
            local_dir=whisper_dir
        )
    else:
        print("Whisper models already exist.")

    print("--- All MuseTalk models downloaded and verified ---")

if __name__ == "__main__":
    download_musetalk_models()
