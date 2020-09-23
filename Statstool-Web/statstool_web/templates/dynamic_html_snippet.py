


def write_html_block(institution1,institution2,label1,label2,start_year = None):
    return """
        <div class="col-md-4">
        <div class="card mb-4 shadow-sm">
        <div class="card-body">
          {{% if savegame_dict["{0}"] and savegame_dict["{2}"] %}}
            <h4 class="card-text">{1}: {{{{savegame_dict["{0}"].year}}}}-{{{{savegame_dict["{2}"].year}}}}</h4>
          {{% elif savegame_dict["{0}"] %}}
            <h4 class="card-text">{1}: {{{{savegame_dict["{0}"].year}}}}-???</h4>
          {{% else %}}
            <h4 class="card-text">{1}: ???-???</h4>
          {{% endif %}}
        </div>
        {{% if savegame_dict["{2}"].map_file %}}
          <div class="media">
            <img src="/static/maps/{{{{savegame_dict['{2}'].map_file}}}}">
          </div>
        {{% endif %}}
        <div class="text-center">
          {{% if savegame_dict["{0}"] and savegame_dict["{2}"] %}}
            {{% if not savegame_dict["{0}"].map_file %}}
              <a class="btn btn-outline-primary btn-center mt-2 mb-2" href = "{{{{url_for('upload_map', sg_id = savegame_dict['{2}'].id)}}}}">Add Map</a>
            {{% endif %}}
            <a class="btn btn-outline-primary btn-center mt-2 mb-2" href = "{{{{url_for('main', sg_id1 = savegame_dict['{0}'].id, sg_id2 = savegame_dict['{2}'].id )}}}}">View</a>
          {{% endif %}}
          {{% if not savegame_dict["{0}"] %}}
            <a class="btn btn-outline-primary btn-center mt-2 mb-2" href = "{{{{url_for('upload_one_savegame', institution = '{0}')}}}}">Add {1}-Savegame</a>
          {{% endif %}}
          {{% if not savegame_dict["{2}"] %}}
            <a class="btn btn-outline-primary btn-center mt-2 mb-2" href = "{{{{url_for('upload_one_savegame', institution = '{2}')}}}}">Add {3}-Savegame</a>
          {{% endif %}}
        </div>
        </div>
        </div>
        """.format(institution1,label1,institution2,label2)


with open("Statstool-Web\statstool_web\templates\html-snippet.html", "w") as file:
    file.write(write_html_block("industrialization", "endsave", "Industrialiserung", "End"))
