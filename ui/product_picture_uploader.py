import tkinter as tk
from tkinter import filedialog, messagebox
from soap.soap_client import DandomainSOAPClient
from image_tools.upload_to_imagebb import upload_image_to_imgbb  # Assuming you have this setup
import os


def upload_picture(image_path):
    """
    Uploads an image to imgbb and returns the URL of the uploaded image.
    """
    response = upload_image_to_imgbb(image_path)
    print(f"Response from imgbb: {response}")
    return response


class ProductPictureUploader:
    def __init__(self, root, product_id):
        self.root = root
        self.root.title("Upload Product Picture")

        self.product_id = product_id
        self.soap_client = DandomainSOAPClient()

        # Image selection button
        tk.Label(root, text="Choose Product Image (.jpg/.png)").pack(padx=10, pady=(10, 5))
        self.select_btn = tk.Button(root, text="Select Image", command=self.select_image)
        self.select_btn.pack(pady=(0, 10))

        self.selected_file_label = tk.Label(root, text="", fg="blue")
        self.selected_file_label.pack(pady=(0, 10))

        # Upload button
        self.upload_btn = tk.Button(root, text="Upload Picture", command=self.upload_picture, state=tk.DISABLED)
        self.upload_btn.pack(pady=10)

        self.image_path = None

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_path = file_path
            self.selected_file_label.config(text=os.path.basename(file_path))
            self.upload_btn.config(state=tk.NORMAL)

    def upload_picture(self):
        try:
            if not self.image_path:
                raise ValueError("No image selected.")

            # Step 1: Upload to imgbb
            image_url = upload_picture(self.image_path)

            # Step 2: Send image URL to SOAP backend
            response = self.soap_client.upload_product_picture(
                product_id=self.product_id,
                image_path=image_url,
                sort=1
            )

            print(f"SOAP response: {response}")
            messagebox.showinfo("Success", "Product picture uploaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


# Function to launch this window
def launch_picture_uploader(product_id):
    root = tk.Tk()
    app = ProductPictureUploader(root, product_id)
    root.mainloop()
