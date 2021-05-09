from flask import render_template, url_for, request, redirect, flash, abort, Blueprint, current_app
from statstool_web.main.forms import *
from statstool_web.main.outsource import *
from statstool_web import db, bcrypt
from statstool_web.parserfunctions import edit_parse
from statstool_web.models import *
from statstool_web.util import redirect_url
from pathlib import Path
from sqlalchemy import desc
from flask_login import login_user, logout_user, current_user, login_required
from math import ceil


import os
import secrets

main = Blueprint('main', __name__)

@main.route("/", methods = ["GET"], defaults = {'mp_id': 3})
@main.route("/home/<int:mp_id>", methods = ["GET"])
def home(mp_id):
    institutions = ["basesave", "renaissance", "colonialism", "printing_press", "global_trade", "manufactories", "enlightenment", "industrialization", "endsave"]
    savegame_dict = {}
    for inst in institutions:
        savegame_dict[inst] = Savegame.query.filter_by(mp_id=mp_id, institution=inst).first()
    mps = MP.query.all()
    current_mp = MP.query.get(mp_id)
    teams = sorted(current_mp.teams, key = lambda team: team.id)
    savegames = Savegame.query.filter_by(mp_id = mp_id).order_by(desc(Savegame.year))
    current_save = savegames.first()
    savegames = list(savegames)

    names_dict = {}
    nation_names_dict = {}
    if current_save:
        for nation in current_save.player_nations:
            nation_data = NationSavegameData.query.filter_by(savegame_id = current_save.id, nation_tag = nation.tag).first()
            if nation_data:
                nation_names_dict[nation.tag] = nation_data.nation_name
                if nation_data.player_name:
                    names_dict[nation_data.nation_name] = nation_data.player_name
                else:
                    names_dict[nation_data.nation_name] = "???"
            else:
                print(nation.tag)
    return render_template("main/home.html", savegames = savegames, counter = len(savegames), \
            savegame_dict = savegame_dict, mps = mps, current_mp = current_mp, teams = teams, \
            current_save = current_save, names_dict = names_dict, nation_names_dict = nation_names_dict)

@main.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
            flash("You have been logged in!", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Login Unsuccessful. Please check username and password.", "danger")
    return render_template("main/login.html", title = "Log In", form = form)

@main.route("/logout", methods = ["GET", "POST"])
def logout():
    logout_user()
    flash(f'Logout successful!', 'success')
    return redirect(url_for("main.home"))

@main.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in.', 'success')
        return redirect(url_for("main.login"))
    return render_template("main/register.html", title = "Register", form = form)


@main.route("/upload_savegames", methods = ["GET", "POST"], defaults = {'mp_id': None})
@main.route("/upload_savegames/<int:mp_id>", methods = ["GET", "POST"])
@login_required
def upload_savegames(mp_id = None):
    mp = MP.query.get(mp_id)
    if (mp_id and mp.admin != current_user):
        abort(403)
    form = SavegameSelectForm()
    if form.validate_on_submit():
        sg_ids = []
        Path(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        for file, map_file, name in zip((request.files[form.savegame1.name],request.files[form.savegame2.name]),\
                            (request.files[form.savegame1_map.name],request.files[form.savegame2_map.name]),(form.savegame1_name.data, form.savegame2_name.data)):
            random = secrets.token_hex(8) + ".eu4"
            path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], random)
            file.save(path)

            if map_file:
                map_random = secrets.token_hex(8) + ".png"
                map_path = os.path.join(current_app.root_path, "static/maps", map_random)
                map_file.save(map_path)
            else:
                map_path = None
            try:
                player_names_dict, tag_list, year = edit_parse(path)
                if map_path:
                    savegame = Savegame(file = random, map_file = map_random, owner = current_user, year = year, name = name)
                else:
                    savegame = Savegame(file = random, owner = current_user, year = year, name = name)
                for tag in tag_list:
                    if not Nation.query.get(tag):
                        nation = Nation(tag = tag)
                        db.session.add(nation)
                        db.session.commit()

                    savegame.nations.append(Nation.query.get(tag))
                    if tag in player_names_dict.keys():
                        savegame.player_nations.append(Nation.query.get(tag))
                        player_name = player_names_dict[tag]
                    else:
                        player_name = None

                    nation_data = NationSavegameData(savegame_id = savegame.id, nation_tag = tag, player_name = player_name)
                    db.session.add(nation_data)

                db.session.add(savegame)
                db.session.commit()
                sg_ids.append(savegame.id)
            except AttributeError as e:
                print(e)
            except (IndexError, UnicodeDecodeError) as e:
                print(e)

        return redirect(url_for("parse.setup", sg_id1 = sg_ids[0], sg_id2 = sg_ids[1], part = 0))
    return render_template("main/upload_savegames.html", form = form)

@main.route("/upload_one_savegame", methods = ["GET", "POST"], defaults={'mp_id': None, 'institution': None})
@main.route("/upload_one_savegame/<int:mp_id>", methods = ["GET", "POST"], defaults={'institution': None})
@main.route("/upload_one_savegame/<int:mp_id>/<string:institution>", methods = ["GET", "POST"])
@login_required
def upload_one_savegame(mp_id, institution):
    mp = MP.query.get(mp_id)
    if (mp_id and mp.admin != current_user):
        abort(403)
    form = OneSavegameSelectForm()
    if form.validate_on_submit():
        Path(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        save_file = request.files[form.savegame.name]
        map_file = request.files[form.map.name]

        random = secrets.token_hex(8) + ".eu4"
        path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], random)
        save_file.save(path)

        if map_file:
            map_random = secrets.token_hex(8) + ".png"
            map_path = os.path.join(current_app.root_path, "static/maps", map_random)
            map_file.save(map_path)
        else:
            map_path = None
        try:
            player_names_dict, tag_list, year = edit_parse(path)
            if map_path:
                savegame = Savegame(file = random, mp_id = mp_id, map_file = map_random, institution = institution, owner = current_user, year = year, name = form.savegame_name.data)
            else:
                savegame = Savegame(file = random, mp_id = mp_id, institution = institution, owner = current_user, year = year, name = form.savegame_name.data)
            for tag in tag_list:
                if not Nation.query.get(tag):
                    nation = Nation(tag = tag)
                    db.session.add(nation)

                savegame.nations.append(Nation.query.get(tag))
                if tag in player_names_dict.keys():
                    savegame.player_nations.append(Nation.query.get(tag))
                    player_name = player_names_dict[tag]
                else:
                    player_name = None

                nation_data = NationSavegameData(savegame_id = savegame.id, nation_tag = tag, player_name = player_name)
                db.session.add(nation_data)


            db.session.add(savegame)
            db.session.commit()
        except AttributeError as e:
            print(e)
        except (IndexError, UnicodeDecodeError) as e:
            print(e)
        else:
            return redirect(url_for("parse.setup", sg_id1 = savegame.id, sg_id2 = savegame.id, part = 0))
    return render_template("main/upload_one_savegame.html", form = form)

@main.route("/upload_map/<int:sg_id>", methods = ["GET", "POST"])
@login_required
def upload_map(sg_id):
    form = MapSelectForm()
    if form.validate_on_submit():
        Path(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        map_file = request.files[form.map.name]
        map_random = secrets.token_hex(8) + ".png"
        map_path = os.path.join(current_app.root_path, "static/maps", map_random)
        map_file.save(map_path)
        savegame = Savegame.query.get(sg_id)
        savegame.map_file = map_random
        db.session.commit()
        return redirect(url_for("main.home"))
    return render_template("main/upload_map.html", form = form)

@main.route("/account/<int:user_id>", methods = ["GET", "POST"])
@login_required
def account(user_id):
    savegames = Savegame.query.filter_by(user_id=user_id).all()
    mps = MP.query.filter_by(admin_id=user_id).all()
    header_labels = ["ID", "MP-Name", "Name", "Year", "Filename", "Map", "Delete"]
    mp_header_labels = ["ID", "Name", "Description", "Spielleiter", "Host", "Settings", "Delete"]
    ids = []
    mp_ids = []
    data = []
    mp_names = []
    mp_descriptions = []
    mp_gms = []
    mp_hosts = []
    maps = []
    mp_form = MPForm()
    for sg in savegames:
        ids.append(sg.id)
        if sg.mp:
            data.append([sg.mp.name, sg.name, sg.year, sg.file])
        else:
            data.append([None, sg.name, sg.year, sg.file])
        maps.append(sg.map_file)
    for mp in mps:
        mp_ids.append(mp.id)
        mp_names.append(mp.name)
        mp_descriptions.append(mp.description)
        mp_gms.append(mp.gm)
        mp_hosts.append(mp.host)
    if mp_form.validate_on_submit():
        so_mp = MP(name = mp_form.mp_name.data, description = mp_form.mp_description.data,\
                gm = mp_form.gm.data, host = mp_form.host.data, checksum = mp_form.checksum.data,\
                next_gameday = mp_form.next_gameday.data, institutions = mp_form.institutions.data,\
                victory_points = mp_form.victory_points.data, teams_setting = mp_form.teams_setting.data,\
                admin = current_user)
        db.session.add(so_mp)
        db.session.commit()
        mp_form.mp_name.data = ""
        mp_form.mp_description.data = ""
        flash(f'Successfully created MP.', 'success')
        return redirect(url_for("main.account", user_id = user_id))
    return render_template("main/account.html", data = zip(ids,data,maps), \
            header_labels = header_labels, mp_header_labels = mp_header_labels, \
            mp_data = zip(mp_ids,mp_names,mp_descriptions, mp_gms, mp_hosts), \
            form = mp_form, user_id = user_id)

@main.route("/delete_savegame/<int:sg_id>", methods = ["GET", "POST"])
@login_required
def delete_savegame(sg_id):
    savegame = Savegame.query.get(sg_id)
    if savegame:
        db.session.delete(savegame)
        db.session.commit()
    return redirect(redirect_url())


@main.route("/settings_mp/<int:user_id>/<int:mp_id>", methods = ["GET", "POST"])
@login_required
def settings_mp(user_id, mp_id):
    form = MPForm()
    mp = MP.query.get(mp_id)
    if request.method == "GET":
        form.mp_name.data = mp.name
        form.mp_description.data = mp.description
        form.gm.data = mp.gm
        form.host.data = mp.host
        form.checksum.data = mp.checksum
        form.next_gameday.data = mp.next_gameday
        form.institutions.data = mp.institutions
        form.victory_points.data = mp.victory_points
        form.teams_setting.data = mp.teams_setting
    if form.validate_on_submit():
        mp.name = form.mp_name.data
        mp.description = form.mp_description.data
        mp.gm = form.gm.data
        mp.host = form.host.data
        mp.checksum = form.checksum.data
        mp.next_gameday = form.next_gameday.data
        mp.institutions = form.institutions.data
        mp.victory_points = form.victory_points.data
        mp.teams_setting = form.teams_setting.data
        db.session.commit()
        flash(f'Successfully updated MP.', 'success')
        return redirect(url_for("main.account", user_id = user_id))
    return render_template("main/mp_settings.html", form = form)

@main.route("/delete_mp/<int:mp_id>", methods = ["GET", "POST"])
@login_required
def delete_mp(mp_id):
    mp = MP.query.get(mp_id)
    if mp:
        db.session.delete(mp)
        db.session.commit()
    return redirect(redirect_url())


@main.route("/total_victory_points/<int:mp_id>", methods = ["GET"])
def total_victory_points(mp_id):
    savegame = Savegame.query.filter_by(mp_id = mp_id).order_by(desc(Savegame.year)).first()
    current_mp = MP.query.get(mp_id)

    if savegame:
        nation_tags = [x.tag for x in savegame.player_nations]
        nation_names = [NationSavegameData.query.filter_by(savegame_id = savegame.id, nation_tag = tag).first().nation_name for tag in nation_tags]
        nation_colors_hex = [NationSavegameData.query.filter_by(nation_tag = tag, \
                    savegame_id = savegame.id).first().color for tag in nation_tags]
        nation_colors_hsl = [NationSavegameData.query.filter_by(nation_tag = tag, \
                    savegame_id = savegame.id).first().color.hsl for tag in nation_tags]


        if mp_id == 3:
            header_labels = ["Team", "Provinzen", "Kolonialismus", "Druckerpresse", \
            "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialisierung", \
            "erster Spielerkrieg-Sieger", "Globaler Handel-Sieger", "Gesamt"]
            institutions = ("colonialism", "printing_press", "global_trade", "manufactories", "enlightenment", "industrialization")
            two_vp_province_ids = {382: "Damaskus", 227: "Lissabon", 333: "Majorca",\
                    1765: "Sofia", 177: "Maine", 45: "Lübeck", 257: "Warschau", 295: "Moskau"}
            one_vp_province_ids = {361: "Kairo", 223: "Granada", 151: "Konstantinopel",\
                    341: "Tunis", 231: "Porto", 170: "Finistère", 183: "Paris", 50: "Berlin",\
                    153: "Pest", 1756: "Bessarabien", 4142: "Ostjylland", 41: "Königsberg"}

            teams = MP.query.get(mp_id).teams
            team_names = []
            for team in teams:
                team_names.append("Team {}".format(team.id))
            team_colors_hex = ["#ffffff"]*len(teams)
            team_colors_hsl = [(0,0,100)]*len(teams)
            data = {}
            for team in teams:
                data[team.id] = [0]*(len(header_labels)-2)

            for institution, column in zip(institutions, range(1,7)):
                for team in teams:
                    if (result := VictoryPoint.query.filter_by(mp_id = mp_id, category = institution, team_id = team.id).first()):
                        data[team.id][column] = result.points

            province_points_dict = {}
            team_province_dict = {team.id: [[],[]] for team in teams}
            free_provinces_one_vp = [x for x in one_vp_province_ids.values()]
            free_provinces_two_vp = [x for x in two_vp_province_ids.values()]
            for team in teams:
                if (vp := VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team.id, category = "provinces").first()):
                    vp.points = 0
                    province_points_dict[team.id] = vp
                else:
                    vp = VictoryPoint(mp_id = mp_id, team_id = team.id, category = "provinces", points = 0)
                    db.session.add(vp)
                    province_points_dict[team.id] = vp
            for (id,name) in two_vp_province_ids.items():
                ProviceData = NationSavegameProvinces.query.filter_by(savegame_id = savegame.id, province_id = id).first()
                owner = ProviceData.nation_tag
                for team in teams:
                    if owner in (team.team_tag1, team.team_tag2):
                        province_points_dict[team.id].points += 2
                        team_province_dict[team.id][0].append(name)
                        free_provinces_two_vp.remove(name)
            for (id,name) in one_vp_province_ids.items():
                ProviceData = NationSavegameProvinces.query.filter_by(savegame_id = savegame.id, province_id = id).first()
                owner = ProviceData.nation_tag
                for team in teams:
                    if owner in (team.team_tag1, team.team_tag2):
                        province_points_dict[team.id].points += 1
                        team_province_dict[team.id][1].append(name)
                        free_provinces_one_vp.remove(name)

            db.session.commit()

            for team in teams:
                data[team.id][0] = VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team.id, category = "provinces").first().points
                vp = VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team.id, category = "first_player_war").first()
                if vp:
                    data[team.id][-2] = vp.points
                vp = VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team.id, category = "global_trade_spawn").first()
                if vp:
                    data[team.id][-1] = vp.points
                data[team.id].append(sum(data[team.id]))
            
            num_free_rows = max([ceil(len(free_provinces_one_vp)/3), ceil(len(free_provinces_two_vp)/3)])
            team_ids = [team.id for team in teams]

            return render_template("main/victory_points.html", header_labels = header_labels,\
                    num_columns = len(header_labels),\
                    nation_info = zip(team_names,team_ids,team_colors_hex,team_colors_hsl), \
                    team_province_dict = team_province_dict, \
                    free_provinces_one_vp = free_provinces_one_vp, \
                    free_provinces_two_vp = free_provinces_two_vp, \
                    num_free_rows = num_free_rows, \
                    data = data, mp_id = mp_id, current_mp = current_mp)


        elif mp_id == 2:
            header_labels, data = mp2_data(nation_tags, mp_id)

            return render_template("main/victory_points.html", header_labels = header_labels,\
                    num_columns = len(header_labels),\
                    nation_info = zip(nation_names,nation_tags,nation_colors_hex,nation_colors_hsl), \
                    data = data, mp_id = mp_id, current_mp = current_mp)

        elif mp_id == 1:
            header_labels, data = mp1_data()

            return render_template("main/victory_points.html", header_labels = header_labels,\
                    num_columns = len(header_labels),\
                    nation_info = zip(nation_names,nation_tags,nation_colors_hex,nation_colors_hsl), \
                    data = data, mp_id = mp_id, current_mp = current_mp)

    else:
        flash(f'Noch keine Siegpunkte vergeben.', 'danger')
        return redirect(url_for("main.home", mp_id = mp_id))

@main.route("/edit_victory_points/<int:mp_id>/<int:team_id>", methods = ["GET", "POST"])
def edit_victory_points(mp_id, team_id):
    form = EditVPForm()
    categories = ["first_player_war", "global_trade_spawn"]
    fields =  [form.first_player_war, form.global_trade_spawn]
    if request.method == "GET":
        for (cat,field) in zip(categories,fields):
            vp = VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team_id, category = cat).first()
            if vp:
                if vp.points == 1:
                    field.data = True
            else:
                field.data = False
    if request.method == "POST":
        for (cat,field) in zip(categories,fields):
            vp = VictoryPoint.query.filter_by(mp_id = mp_id, team_id = team_id, category = cat).first()
            if not vp:
                vp = VictoryPoint(mp_id = mp_id, team_id = team_id, category = cat)
                db.session.add(vp)
            if field.data:
                vp.points = 1
            else:
                vp.points = 0

        db.session.commit()
        return redirect(url_for("main.total_victory_points", mp_id = mp_id))
    return render_template("main/edit_vps.html", form = form, mp_id = mp_id)

@main.route("/latest_stats/<int:mp_id>", methods = ["GET"])
def latest_stats(mp_id):
    savegames = Savegame.query.filter_by(mp_id = mp_id).order_by(desc(Savegame.year)).all()
    if len(savegames) > 1:
        sg_id1 = savegames[1].id
        sg_id2 = savegames[0].id
        return redirect(url_for("show_stats.parse", sg_id1 = sg_id1, sg_id2 = sg_id2, part = 0))
    else:
        flash(f'Noch keine Statistik verfügbar.', 'danger')
        return redirect(url_for("main.home", mp_id = mp_id))

@main.route("/configure_teams/<int:mp_id>", methods = ["GET", "POST"])
def configure_teams(mp_id):
    form = ConfigureTeamsForm()
    mp = MP.query.get(mp_id)
    teams = sorted(mp.teams, key = lambda team: team.id)
    if request.method == "POST":
        return redirect(url_for("main.home", mp_id = mp_id))
    return render_template("main/configure_teams.html", form = form, mp = mp, teams = teams)

@main.route("/add_team/<int:mp_id>", methods = ["GET", "POST"])
def add_team(mp_id):
    form = NewTeamForm()
    if request.method == "POST":
        team = Team(id = form.id.data, mp_id = mp_id, team_tag1 = form.select1.data, team_tag2 = form.select2.data)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for("main.configure_teams", mp_id = mp_id))
    return render_template("main/new_team.html", form = form, mp_id = mp_id)

@main.route("/delete_team/<int:mp_id>/<int:team_id>", methods = ["GET"])
def delete_team(mp_id, team_id):
    team = Team.query.get((team_id, mp_id))
    if team:
        db.session.delete(team)
        db.session.commit()
    return redirect(redirect_url())

@main.route("/add_mp_map/<int:mp_id>", methods = ["GET", "POST"])
def add_mp_map(mp_id):
    form = MapSelectForm()
    if form.validate_on_submit():
        Path(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        map_file = request.files[form.map.name]
        map_random = secrets.token_hex(8) + ".png"
        map_path = os.path.join(current_app.root_path, "static/maps", map_random)
        map_file.save(map_path)
        mp = MP.query.get(mp_id)
        mp.map_file = map_random
        db.session.commit()
        return redirect(url_for("main.home", mp_id = mp_id))
    return render_template("main/upload_map.html", form = form)

@main.route("/add_current_mp_map/<int:mp_id>", methods = ["GET", "POST"])
def add_current_mp_map(mp_id):
    form = MapSelectForm()
    if form.validate_on_submit():
        Path(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])).mkdir(parents=True, exist_ok=True)
        map_file = request.files[form.map.name]
        map_random = secrets.token_hex(8) + ".png"
        map_path = os.path.join(current_app.root_path, "static/maps", map_random)
        map_file.save(map_path)
        mp = MP.query.get(mp_id)
        mp.current_map_file = map_random
        db.session.commit()
        return redirect(url_for("main.home", mp_id = mp_id))
    return render_template("main/upload_map.html", form = form)

@main.route("/delete_mp_map/<int:mp_id>", methods = ["GET"])
def delete_mp_map(mp_id):
    mp = MP.query.get(mp_id)
    try:
        os.remove(os.path.join(current_app.root_path, 'static/maps', mp.map_file))
    except FileNotFoundError:
        pass
    mp.map_file = None
    db.session.commit()
    return redirect(redirect_url())

@main.route("/delete_current_mp_map/<int:mp_id>", methods = ["GET"])
def delete_current_mp_map(mp_id):
    mp = MP.query.get(mp_id)
    try:
        os.remove(os.path.join(current_app.root_path, 'static/maps', mp.current_map_file))
    except FileNotFoundError:
        pass
    mp.current_map_file = None
    db.session.commit()
    return redirect(redirect_url())

@main.route('/colorize.js')
def colorize():
    return render_template('jquery-colorize.js')
