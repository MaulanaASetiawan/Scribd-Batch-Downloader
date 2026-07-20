import os
import re
import time
import shutil
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class ScribdDownloaderLogic:
    def __init__(self, log_cb, progress_cb, status_cb, finish_cb):
        self.log_cb = log_cb
        self.progress_cb = progress_cb
        self.status_cb = status_cb
        self.finish_cb = finish_cb
        self.is_cancelled = False
        
        self.base_dir = os.getcwd()
        self.download_dir = os.path.join(self.base_dir, "Scribd_Downloads")
        self.thumb_dir = os.path.join(self.download_dir, ".thumbnails")
        self.temp_dir = os.path.join(self.download_dir, "temp_images")

        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.thumb_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.scribd.com/"
        })

    def cancel_download(self):
        self.is_cancelled = True

    def sanitize_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "", name).strip()
        
    def _clear_temp_dir(self):
        """Pembersih folder temp agar tidak menumpuk memenuhi memori"""
        for filename in os.listdir(self.temp_dir):
            filepath = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
            except Exception:
                pass

    def process_batch(self, doc_ids):
        self.is_cancelled = False
        for index, doc_id in enumerate(doc_ids):
            if self.is_cancelled:
                self.log_cb("\n[DIBATALKAN] Proses antrean dihentikan.", "danger")
                break

            self.log_cb(f"==================================================")
            self.log_cb(f"[*] MEMPROSES DOKUMEN {index+1} DARI {len(doc_ids)} (ID: {doc_id})", "text_main")
            self.log_cb(f"==================================================")
            
            self.progress_cb(0, 100)
            self.status_cb(f"Status: Dokumen {index+1}/{len(doc_ids)} - Memulai browser...")
            
            self.download_single(doc_id, index + 1, len(doc_ids))
            
            if self.is_cancelled:
                self.log_cb("\n[DIBATALKAN] Proses pengunduhan dihentikan.", "danger")
                break
                
            time.sleep(2) 
            
        if not self.is_cancelled:
            self.log_cb(f"\n[SELESAI] Semua {len(doc_ids)} dokumen telah diproses!", "text_main")
            self.status_cb("Status: Semua antrean selesai!")
        else:
            self.status_cb("Status: Dibatalkan!")
            
        self.finish_cb()

    def download_single(self, doc_id, current_doc, total_docs):
        if self.is_cancelled: return
        
        self._clear_temp_dir()

        target_url = f"https://www.scribd.com/embeds/{doc_id}/content?start_page=1&view_mode=scroll"
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.log_cb(f"[ERROR] Gagal membuka browser: {e}", "danger")
            return

        driver.get(target_url)
        self.log_cb("[!] Menunggu 15 detik. JIKA MUNCUL CAPTCHA, SELESAIKAN DI BROWSER!", "accent")
        
        for _ in range(15):
            if self.is_cancelled:
                driver.quit()
                return
            time.sleep(1)

        rendered_html = driver.page_source
        fallback_title = driver.title.replace(" - Scribd", "").strip()
        driver.quit()

        title_pattern = rf'scribd\.com/document/{doc_id}/([^/"\']+)'
        title_match = re.search(title_pattern, rendered_html)
        
        if title_match:
            raw_title = title_match.group(1).replace('-', ' ')
        else:
            raw_title = fallback_title
            
        doc_title = self.sanitize_filename(raw_title)
        if not doc_title:
            doc_title = f"Document_{doc_id}"
            
        self.log_cb(f"[*] Judul: {doc_title}")

        cover_url = None
        cover_match = re.search(r'<meta\s+(?:name|property)=["\']og:image["\']\s+content=["\']([^"\']+)["\']', rendered_html)
        if not cover_match:
            cover_match = re.search(r'content=["\']([^"\']+)["\']\s+(?:name|property)=["\']og:image["\']', rendered_html)
        if cover_match:
            cover_url = cover_match.group(1)

        direct_img_pattern = r'orig=["\'](https?://[^"\']+?\.(?:jpg|jpeg|png))["\']'
        direct_img_urls = list(dict.fromkeys(re.findall(direct_img_pattern, rendered_html)))

        jsonp_pattern = r'(https?://[^\s"\'<>]+?\.jsonp(?:[^\s"\'<>]*)?)'
        jsonp_urls = list(dict.fromkeys(re.findall(jsonp_pattern, rendered_html)))

        total_pages = len(direct_img_urls) + len(jsonp_urls)

        if total_pages == 0:
            self.log_cb("[ERROR] Halaman tidak ditemukan.", "danger")
            return

        self.log_cb(f"[*] Ditemukan {total_pages} halaman (Di luar cover).")
        downloaded_images = []
        
        if cover_url and not self.is_cancelled:
            self.log_cb("[*] Mengunduh gambar Cover...", "accent")
            try:
                cover_data = self.session.get(cover_url).content
                cover_path = os.path.join(self.temp_dir, "page_0_cover.jpg")
                with open(cover_path, 'wb') as f:
                    f.write(cover_data)
                downloaded_images.append(cover_path)
            except Exception as e:
                self.log_cb(f"    -> Gagal unduh cover: {e}", "danger")
        
        self.log_cb("[*] Mulai mengunduh gambar halaman...", "accent")
        current_page_idx = 1
        
        for img_url in direct_img_urls:
            if self.is_cancelled: break
            try:
                img_data = self.session.get(img_url).content
                img_path = os.path.join(self.temp_dir, f"page_{current_page_idx}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                downloaded_images.append(img_path)
                
                percent = int((current_page_idx / total_pages) * 100)
                self.progress_cb(current_page_idx, total_pages)
                self.status_cb(f"Status (Dok {current_doc}/{total_docs}): Hal {current_page_idx}/{total_pages} ({percent}%)")
                current_page_idx += 1
            except Exception:
                pass

        for jsonp_url in jsonp_urls:
            if self.is_cancelled: break
            try:
                jsonp_resp = self.session.get(jsonp_url)
                clean_text = jsonp_resp.text.replace('\\/', '/')
                
                img_pattern = r'(https?://[^"\s>]+?\.(?:jpg|jpeg|png))'
                img_urls = re.findall(img_pattern, clean_text)
                
                if img_urls:
                    target_img_url = img_urls[0]
                    if target_img_url in direct_img_urls:
                        total_pages -= 1
                        continue
                        
                    img_data = self.session.get(target_img_url).content
                    img_path = os.path.join(self.temp_dir, f"page_{current_page_idx}.jpg")
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    downloaded_images.append(img_path)
                    
                    percent = int((current_page_idx / total_pages) * 100)
                    self.progress_cb(current_page_idx, total_pages)
                    self.status_cb(f"Status (Dok {current_doc}/{total_docs}): Hal {current_page_idx}/{total_pages} ({percent}%)")
                    current_page_idx += 1
            except Exception:
                pass

        if downloaded_images and not self.is_cancelled:
            self.log_cb("[*] Menyusun halaman menjadi PDF...", "accent")
            self.status_cb(f"Status (Dok {current_doc}/{total_docs}): Memproses PDF...")
            
            pdf_path = os.path.join(self.download_dir, f"{doc_title}.pdf")
            pdf_pages = []
            
            for img_path in downloaded_images:
                try:
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    pdf_pages.append(img)
                except:
                    pass
            
            if pdf_pages:
                pdf_pages[0].save(pdf_path, save_all=True, append_images=pdf_pages[1:])
                
                try:
                    thumb_path = os.path.join(self.thumb_dir, f"{doc_title}_thumb.jpg")
                    shutil.copy(downloaded_images[0], thumb_path)
                except Exception:
                    pass
                
                self.log_cb(f"[SUKSES] Tersimpan: {pdf_path}", "secondary")
                
        self._clear_temp_dir()