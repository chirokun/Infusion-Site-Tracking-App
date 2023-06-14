import tkinter as tk
import csv
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import shutil
import os


class InfusionSiteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Infusion Site App")

        self.canvas = tk.Canvas(self, width=1200, height=800)
        self.canvas.pack()

        self.points = []

        # Load the image
        image_path = "human_figure.png"
        self.load_image(image_path)

        self.bind_events()

        # Create a "Save" button
        save_button = tk.Button(
            self, text="Save", command=self.save_points_to_csv)
        save_button.pack()

        # Create an "Exit" button
        exit_button = tk.Button(self, text="Exit", command=self.close)
        exit_button.pack()

        # Create a label for the input
        expiration_label = tk.Label(self, text ="Expriation (in weeks):")
        expiration_label.pack()

        self.expiration_entry = tk.Entry(self)
        self.expiration_entry.pack()

        # Load points from CSV and draw them on the canvas
        self.load_points_from_csv()

    def close(self):
        self.destroy()

    def load_image(self, image_path):
        image = Image.open(image_path)
        image = image.resize((1200, 800), resample=Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def load_points_from_csv(self):
        self.points = []
        filename = "infusion_site_data.csv"
        # Check if the CSV file exists
        if not os.path.isfile(filename):
            # Create a new CSV file with headers
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Point Number', 'X', 'Y', 'Expiration Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            return  # Exit the method if the CSV file is newly created

        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                point_number_str = row['Point Number']
                if point_number_str.isdigit():
                    point_number = int(point_number_str)
                    x = int(row['X'])
                    y = int(row['Y'])
                    expiration_timestamp = datetime.strptime(
                        row['Expiration Date'], '%m/%d/%Y')
                    self.points.append(
                        (point_number, (x, y), expiration_timestamp))

        # Delete existing points from the canvas
        self.canvas.delete("all")

        # Load the image
        image_path = "human_figure.png"
        self.load_image(image_path)

        # Draw the points on the canvas
        for point in self.points:
            point_number, (x, y), _ = point
            self.draw_point(x, y, point_number)

        # Filter and delete expired points
        self.filter_expired_points()

    def draw_point(self, x, y, point_number):
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")
        self.canvas.create_text(x, y - 10, text=str(point_number), fill="black",
                                tags=("point_text", f"point_{point_number}"))

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-3>", self.delete_point)


    def add_point(self, event):
        x = event.x
        y = event.y

        expiration_weeks = self.expiration_entry.get()

        if not expiration_weeks.isdigit():
            # Handle invalid input
            tk.messagebox.showerror("Invalid Input", "Please Enter a valid number of weeks.")
            return
        
        expiration_weeks = int(expiration_weeks)
        current_time = datetime.now()
        expiration_timestamp = current_time + timedelta(weeks=expiration_weeks)
        point_number = len(self.points) + 1
        self.points.append((point_number, (x, y), expiration_timestamp))
        self.draw_point(x, y, point_number)
        self.filter_expired_points()
        self.expiration_entry.delete(0, tk.END) # Clear the expiration entry field


    def handle_expiration_input(self, input_text, x, y):
        try:
            expiration_weeks = int(input_text)
            current_time = datetime.now()
            expiration_timestamp = current_time + timedelta(weeks=expiration_weeks)
            point_number = len(self.points) + 1
            self.points.append((point_number, (x, y), expiration_timestamp))
            # Draw the point on the canvas
            self.draw_point(x, y, point_number)

            # Filter and delete expired points
            self.filter_expired_points()
        except ValueError:
            # Handle invalid input
            tk.messagebox.showerror(
            "Invalid Input", "Please enter a valid number of weeks.")

    def delete_point(self, event):
        # Get the closest point to the mouse click coordinates
        closest_item = self.canvas.find_closest(event.x, event.y)
        if closest_item:
            item_tags = self.canvas.gettags(closest_item)
            point_tags = [tag for tag in item_tags if tag.startswith("point_")]
            if point_tags:
                point_tag = point_tags[0]
                point_number = int(point_tag.split("_")[1])
                # Remove the point from self.points
                self.points = [
                    point for point in self.points if point[0] != point_number]
                # Delete the point from the canvas
                self.canvas.delete(point_tag)

                # Update point numbers after deletion
                self.update_point_numbers()

    def update_point_numbers(self):
        # Delete existing point numbers
        self.canvas.delete("point_text")

        # Draw the updated point numbers
        for i, point in enumerate(self.points, start=1):
            point_number, (x, y), expiration_timestamp = point
            self.draw_point(x, y, i)

    def filter_expired_points(self):
        current_time = datetime.now()
        expired_points = [
            point for point in self.points if point[2] < current_time]
        for expired_point in expired_points:
            point_number, (x, y), _ = expired_point
            point_tag = f"point_{point_number}"
            # Delete the point from the canvas
            self.canvas.delete(point_tag)

        # Remove the expired points from self.points
        self.points = [
            point for point in self.points if point not in expired_points]

        # Update point numbers after filtering
        self.update_point_numbers()

    def save_points_to_csv(self):
        filename = "infusion_site_data.csv"

        # Check if the CSV file exists
        if not os.path.isfile(filename):
            # Create a new CSV file with headers
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Point Number', 'X', 'Y', 'Expiration Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

        backup_filename = "infusion_site_data_backup.csv"  # Backup filename

        # Create a backup of the original CSV file
        shutil.copy2(filename, backup_filename)

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Point Number', 'X', 'Y', 'Expiration Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for point in self.points:
                point_number, (x, y), expiration_timestamp = point
                expiration_date = expiration_timestamp.strftime('%m/%d/%Y')
                writer.writerow({'Point Number': point_number, 'X': x,
                                 'Y': y, 'Expiration Date': expiration_date})


if __name__ == '__main__':
    app = InfusionSiteApp()
    app.mainloop()
