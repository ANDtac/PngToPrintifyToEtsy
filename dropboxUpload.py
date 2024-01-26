from tqdm import tqdm
import os
import dropbox
from dropboxAuthentication import refresh_dropbox_access_token

dropbox_app_key = ''
dropbox_app_secret = ''
dropbox_refresh_token = ''
image_urls = []

def dropbox_upload(image_files):
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks

    # Use the function to get a new access token
    access_token = refresh_dropbox_access_token(dropbox_app_key, dropbox_app_secret, dropbox_refresh_token)

    # Create a new Dropbox object with the new access token.
    dbx = dropbox.Dropbox(access_token)
    print(f'Uploading {len(image_files)} files to Dropbox')

    with tqdm(total=len(image_files), ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}', leave=False) as pbar:
        for i, (image_file_path, subfolder_name) in enumerate(image_files):
            with open(image_file_path, "rb") as image_file:
                pbar.set_description(f"Uploading {os.path.basename(image_file_path)} to Dropbox")

                file_size = os.path.getsize(image_file_path)
                if file_size <= CHUNK_SIZE:
                    dbx.files_upload(image_file.read(), f"/{subfolder_name}/{os.path.basename(image_file_path)}", mode=dropbox.files.WriteMode.overwrite)
                else:
                    upload_session_start_result = dbx.files_upload_session_start(image_file.read(CHUNK_SIZE))
                    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id, offset=image_file.tell())
                    commit = dropbox.files.CommitInfo(path=f"/{subfolder_name}/{os.path.basename(image_file_path)}")

                    while image_file.tell() < file_size:
                        if (file_size - image_file.tell()) <= CHUNK_SIZE:
                            dbx.files_upload_session_finish(image_file.read(CHUNK_SIZE), cursor, commit)
                        else:
                            dbx.files_upload_session_append_v2(image_file.read(CHUNK_SIZE), cursor)
                            cursor.offset = image_file.tell()

                response = dbx.files_get_metadata(f"/{subfolder_name}/{os.path.basename(image_file_path)}")
                link = dbx.sharing_create_shared_link(response.path_display)
                url = link.url.replace('&dl=0', '&dl=1')
                image_urls.append(url)
                pbar.update(1)

        pbar.set_description(f'')
        print("\nUpload to Dropbox complete.")
        return image_urls
