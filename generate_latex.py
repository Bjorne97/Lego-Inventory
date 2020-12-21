import json
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def read_data(file_path):
    f = open(file_path, "r")
    data = f.read()
    f.close()
    return data


def write_data(file_path, data):
    f = open(file_path, "w")
    f.write(data)
    f.close()


def generate_toc_text(data):
    toc_text = ""
    for elem in data:
        toc_text += ("\\"+"toc{"+elem["class"]+"}\n")

    write_data(f"{DIR_PATH}/Latex/lego_toc.tex", toc_text)


def generate_cummulative_table_text(cummulative_info):
    table_text = ""
    all_sets = str(sum([cummulative_info[name]["sets"] for name in cummulative_info]))
    all_unique_sets = str(sum([cummulative_info[name]["unique sets"] for name in cummulative_info]))
    all_pieces = str(sum([cummulative_info[name]["pieces"] for name in cummulative_info]))
    all_price = sum([cummulative_info[name]["price"] for name in cummulative_info])
    all_price_text = "\\"+"$"+f"{all_price:.0f}"
    all_complete = str(sum([cummulative_info[name]["complete"] for name in cummulative_info]))
    all_unique_complete = str(sum([cummulative_info[name]["unique complete"] for name in cummulative_info]))
    all_min_year = str(min([cummulative_info[name]["year"][0] for name in cummulative_info]))
    all_max_year = str(max([cummulative_info[name]["year"][1] for name in cummulative_info]))
    all_year_text = all_min_year+"--"+all_max_year

    table_text += "\\"+"begin{alllegotable}\n"
    for name in cummulative_info:
        sets = str(cummulative_info[name]["sets"])
        unique_sets = str(cummulative_info[name]["unique sets"])
        pieces = str(cummulative_info[name]["pieces"])
        price = cummulative_info[name]["price"]
        price_text = "\\"+"$"+f"{price:.0f}"
        complete = str(cummulative_info[name]["complete"])
        unique_complete = str(cummulative_info[name]["unique complete"])
        year = cummulative_info[name]["year"]
        min_year = str(year[0])
        max_year = str(year[1])
        year_text = f"{min_year}--{max_year}" if min_year != max_year else min_year

        unique_sets = "" if sets == unique_sets else f"({unique_sets})"
        unique_complete = "" if complete == unique_complete else f"({unique_complete})"

        table_text += "\\"+"allelem{"+name+"}{"+pieces+"}{"+price_text+"}{"+sets+"}{"+unique_sets+"}{"+complete+"}{"+unique_complete+"}{"+year_text+"}\n"
        table_text += "\\"+"hline"

    table_text += "\\"+"hline\n"
    table_text += f"All Lego & {all_pieces} & {all_price_text} & {all_sets} & ({all_unique_sets}) & {all_complete} & ({all_unique_complete}) & {all_year_text}"

    table_text += "\\"+"end{alllegotable}\n"
    table_text += "\\"+"newpage\n"
    return table_text


def generate_table_text(data):
    table_text = ""
    left_right = 0

    cummulative_info = {}
    for i, lego_class in enumerate(data):
        class_name = lego_class["class"]
        class_sets = sum([elem["quantity"] for elem in lego_class["sets"]])
        class_unique_sets = len(lego_class["sets"])
        class_pieces = sum([elem["pieces"]*elem["quantity"] for elem in lego_class["sets"]])
        class_price = sum([float(elem["price"][1:])*elem["quantity"] for elem in lego_class["sets"] if elem["price"][0] == "$"])
        class_complete = sum([elem["complete"] for elem in lego_class["sets"] if elem["quantity"] == 1]) + sum([elem["complete amount"] for elem in lego_class["sets"] if elem["quantity"] > 1])
        class_unique_complete = sum([elem["complete"] for elem in lego_class["sets"]])
        class_year = (min([elem["year"] for elem in lego_class["sets"]]), max([elem["year"] for elem in lego_class["sets"]]))
        cummulative_info[class_name] = {"sets": class_sets, "unique sets": class_unique_sets, "pieces": class_pieces, "price": class_price, "complete": class_complete, "unique complete": class_unique_complete, "year": class_year}

        min_year = str(class_year[0])
        max_year = str(class_year[1])
        year_text = f"{min_year}--{max_year}" if min_year != max_year else min_year
        sets_text = f"{class_sets}" if class_sets == class_unique_sets else f"{class_sets} ({class_unique_sets})"
        price_text = "\\"+f"${class_price:.2f}"
        complete_text = f"{class_complete}"+"\\hspace{7pt}\\ " if class_complete == class_unique_complete else f"{class_complete} ({class_unique_complete})"
        sum_text = "\\"+"hline\n"
        sum_text += "\\"+"bfseries Sum&&"+"\\"+"multicolumn{2}{r|}{"+complete_text+"}&"+"\\"+"multicolumn{2}{r|}{"+year_text+"}&"+str(class_pieces)+"&"+price_text+"&"+sets_text+"\n"

        table_text += "\\"+"begin{legotable}{"+class_name+"}\n"

        for elem in lego_class["sets"]:
            name = elem["name"]
            si = str(elem["id"])
            instructions = "Yes" if elem["instructions"] else "No"
            complete = ("Yes" if elem["complete"] else "No") if elem["quantity"] == 1 else str(elem["complete amount"])
            bagged = "Yes" if elem["bagged"] else "No"
            year = str(elem["year"])
            pieces = str(elem["pieces"])
            quantity = str(elem["quantity"])
            price = elem["price"].split()[0]
            if price[0] == "$":
                price = "\\"+price

            elem_text = "\\"+"elem{"+name+"}{"+si+"}{"+instructions+"}{"+complete+"}{"+bagged+"}{"+year+"}{"+pieces+"}{"+quantity+"}{"+price+"}\n"
            elem_text += "\\"+"hline\n"
            table_text += elem_text

        if class_sets != 1:
            table_text += sum_text
        table_text += "\\"+"end{legotable}\n"

    table_text = generate_cummulative_table_text(cummulative_info) + table_text

    write_data(f"{DIR_PATH}/Latex/lego_tables.tex", table_text)


def generate_image_text(data):
    image_text = ""
    for i, lego_class in enumerate(data):
        class_name = lego_class["class"]
        if len(lego_class["sets"]) > 4:
            image_text += "\\"+"newpage\n"
        else:
            image_text += "\\"+"vspace{2.5cm}\n"

        image_text += "\\"+"section*{"+"\\"+"centering "+"\\"+"hyperref[contents]{"+class_name+"}}"+"\\"+"label{image:"+class_name+"}\n"

        lego_sets = lego_class["sets"]

        count = 0
        for ls in lego_sets:
            si = ls["id"]
            name = ls["name"]
            quantity = ls["quantity"]
            q = str(quantity) + "x" if quantity is not 1 else ""
            if count == 0:
                image_text += "\\"+"begin{figure}[H]"+"\\"+"begin{flushleft}\n"

            image_text += "\\"+"image{"+str(si)+"}{"+name+"}{"+q+"}\n"

            if count == 3:
                image_text += "\\"+"end{flushleft}"+"\\"+"end{figure}\n"
                count = 0
            else:
                count += 1

        if count > 0:
            image_text += "\\"+"end{flushleft}"+"\\"+"end{figure}\n"



    write_data(f"{DIR_PATH}/Latex/lego_images.tex", image_text)


def fix_data(data):
    for lego_class in data:
        for ls in lego_class["sets"]:
            name = ls["name"]
            new_name = name.split(" (")[0].split(" - ")[0]
            ls["name"] = new_name


    sorted_data = sorted(data, key=lambda lego_class: -len(lego_class["sets"]))
    return sorted_data




def main():
    data = json.loads(read_data(f"{DIR_PATH}/lego_sets_all_data.json"))
    data = fix_data(data)
    generate_toc_text(data)
    generate_table_text(data)
    generate_image_text(data)
    print("Successfully generated tex files")


if __name__ == '__main__':
    main()
