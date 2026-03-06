try:
    from huggingface_hub import HfApi
    print("Hugging Face 库已成功安装！")
except ImportError:
    print("仍然找不到库，请检查 Python 解释器设置。")