import shutil, os
src=r'c:\Users\Asus\Desktop\cingilweb_full\www.ruyaajansorganizasyon.com\images\ana-sayfa\slider\1.jpg'
dst_dir=r'c:\Users\Asus\Desktop\cingilweb\assets\images\ana-sayfa\slider'
os.makedirs(dst_dir, exist_ok=True)
dst=os.path.join(dst_dir, os.path.basename(src))
shutil.copy2(src,dst)
print('copied', dst)
