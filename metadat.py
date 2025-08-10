class Mettadata:
 def get_sonnar_id_from_title(self, title):
    return f"sonnarr/{title}"

 def get_metadata(sonnar_id):
   return(sonnar_id)

if __name__ == "__main__":
   # Example
   m= Mettadata()
   print(m.get_sonnar_id_from_title("anime_name"))