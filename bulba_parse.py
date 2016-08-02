"""Parses Bulbapedia's table of Pokemon ordered by National Dex number. Writes result into a text file that can be converted to a list."""

def get_pokemon_list():
    with open('pokemon_list.txt', 'r') as list_file:
        pokemon_list = list_file.read().split()
    return pokemon_list

def bulba_parse():
    is_first_name = True

    with open('bulbapedia.txt', 'r') as bulba_file, open('pokemon_list.txt', 'w') as list_file:
        for line in bulba_file:
            split_line = line.split('|')
            if len(split_line) >= 4 and split_line[0] == '{{rdex':
                if not is_first_name:
                    list_file.write(' ')
                list_file.write(split_line[3].lower())
                is_first_name = False

if __name__ == '__main__':
    bulba_parse()
    print('Parsed Bulbapedia text file! Output has been placed in pokemon_list.txt.\n' + 
          'You may get a list from it by calling bulba_parse.get_pokemon_list().')