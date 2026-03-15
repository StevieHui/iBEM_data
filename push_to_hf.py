from huggingface_hub import HfApi
import os

# ==== 1. 配置信息 ====
# 注意：我已经将 token 放入 HfApi 初始化中
MY_TOKEN = ""
REPO_ID = "StevieHui/iBEM_data" 
# 建议推送具体的环境场文件夹，而不是整个 ibem_data 大目录，这样仓库结构更清晰
LOCAL_FOLDER = r"D:\陈熠辉备份\大三上\寒假科研\ibem_data"

# 初始化带权限的 API 对象
api = HfApi(token=MY_TOKEN)

# ==== 2. 执行推送 ====
print(f"正在准备推送环境场数据至 https://huggingface.co/datasets/{REPO_ID} ...")

try:
    # 使用 upload_large_folder 处理大量 npz 文件
    api.upload_large_folder(
        folder_path=LOCAL_FOLDER,
        repo_id=REPO_ID,
        repo_type="dataset",
        # 如果你希望在网页端能看到上传进度，可以加上这行（可选）
        print_report=True 
    )
    print("\n--- [成功] 数据集已同步完成！ ---")
except Exception as e:
    print(f"\n--- [失败] 推送过程中出现错误 ---")
    print(f"具体错误信息: {e}")