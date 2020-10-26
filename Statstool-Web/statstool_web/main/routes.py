from flask import render_template, url_for, request, redirect, flash, abort, Blueprint, current_app
from statstool_web.main.forms import SavegameSelectForm, OneSavegameSelectForm, MapSelectForm, LoginForm, RegistrationForm
from statstool_web import db, bcrypt
from statstool_web.parserfunctions import edit_parse
from statstool_web.models import User, MP, Savegame, Nation, NationSavegameData
from statstool_web.util import redirect_url
from pathlib import Path
from sqlalchemy import desc
from flask_login import login_user, logout_user, current_user, login_required

import os
import secrets

main = Blueprint('main', __name__)

@main.route("/", methods = ["GET"])
@main.route("/home", methods = ["GET"])
def home(mp_id = 1):
    institutions = ["basesave", "renaissance", "colonialism", "printing_press", "global_trade", "manufactories", "enlightenment", "industrialization", "endsave"]
    savegame_dict = {}
    for inst in institutions:
        savegame_dict[inst] = Savegame.query.filter_by(mp_id=1, institution=inst).first()
    mps = MP.query.all()
    current_mp = MP.query.get(mp_id)
    return render_template("home.html", savegame_dict = savegame_dict, mps = mps, current_mp = current_mp)

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
    return render_template("login.html", title = "Log In", form = form)

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
    return render_template("register.html", title = "Register", form = form)

@main.route("/upload_savegames", methods = ["GET", "POST"])
@login_required
def upload_savegames():
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
                playertags, tag_list, year = edit_parse(path)
                print(name)
                if map_path:
                    savegame = Savegame(file = random, map_file = map_random, owner = current_user, year = year, name = name)
                else:
                    savegame = Savegame(file = random, owner = current_user, year = year, name = name)
                for tag in tag_list:
                    if not Nation.query.get(tag):
                        if tag in current_app.config["LOCALISATION_DICT"].keys():
                            t = Nation(tag = tag, name = current_app.config["LOCALISATION_DICT"][tag])
                        else:
                            t = Nation(tag = tag, name = tag)
                        db.session.add(t)
                        db.session.commit()

                    savegame.nations.append(Nation.query.get(tag))
                    if tag in playertags:
                        savegame.player_nations.append(Nation.query.get(tag))

                db.session.add(savegame)
                db.session.commit()
                sg_ids.append(savegame.id)
            except AttributeError as e:
                print(e)
            except (IndexError, UnicodeDecodeError) as e:
                print(e)

        return redirect(url_for("parse.setup", sg_id1 = sg_ids[0], sg_id2 = sg_ids[1]))
    return render_template("upload_savegames.html", form = form)

@main.route("/upload_one_savegame", methods = ["GET", "POST"], defaults={'mp_id': None, 'institution': None})
@main.route("/upload_one_savegame/<int:mp_id>/<string:institution>", methods = ["GET", "POST"])
@login_required
def upload_one_savegame(mp_id = None, institution = None):
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
            playertags, tag_list, year = edit_parse(path)
            if map_path:
                savegame = Savegame(file = random, mp_id = mp_id, map_file = map_random, institution = institution, owner = current_user, year = year, name = form.savegame_name.data)
            else:
                savegame = Savegame(file = random, mp_id = mp_id, institution = institution, owner = current_user, year = year, name = form.savegame_name.data)
            for tag in tag_list:
                if not Nation.query.get(tag):
                    if tag in current_app.config["LOCALISATION_DICT"].keys():
                        t = Nation(tag = tag, name = current_app.config["LOCALISATION_DICT"][tag])
                    else:
                        t = Nation(tag = tag, name = tag)
                    db.session.add(t)
                    db.session.commit()

                savegame.nations.append(Nation.query.get(tag))
                if tag in playertags:
                    savegame.player_nations.append(Nation.query.get(tag))

            db.session.add(savegame)
            db.session.commit()
        except AttributeError as e:
            print(e)
        except (IndexError, UnicodeDecodeError) as e:
            print(e)
        return redirect(url_for("parse.setup", sg_id1 = savegame.id, sg_id2 = savegame.id))
    return render_template("upload_one_savegame.html", form = form)

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
    return render_template("upload_map.html", form = form)

@main.route("/account/<int:user_id>", methods = ["GET"])
@login_required
def account(user_id):
    savegames = Savegame.query.filter_by(user_id=user_id).all()
    header_labels = ["ID", "MP-Name", "Name", "Year", "Filename", "Map", "Delete"]
    ids = []
    data = []
    maps = []
    for sg in savegames:
        ids.append(sg.id)
        if sg.mp:
            data.append([sg.mp.name, sg.name, sg.year, sg.file])
        else:
            data.append([None, sg.name, sg.year, sg.file])
        maps.append(sg.map_file)
    return render_template("account.html", data = zip(ids,data,maps), header_labels = header_labels)

@main.route("/delete_savegame/<int:sg_id>", methods = ["GET", "POST"])
@login_required
def delete_savegame(sg_id):
    savegame = Savegame.query.get(sg_id)
    if savegame:
        db.session.delete(savegame)
        db.session.commit()
    return redirect(redirect_url())


@main.route("/total_victory_points/<int:mp_id>", methods = ["GET"])
def total_victory_points(mp_id):
    savegame = Savegame.query.filter_by(mp_id = mp_id).order_by(desc(Savegame.year)).first()

    if savegame:
        header_labels = ["Nation", "Basis", "Kriege", "Renaissance", "Kolonialismus", "Druckerpresse", "Globaler Handel", "Manufakturen", "Aufklärung", "Industrialiserung", "Gesamt"]
        nation_tags = [x.tag for x in savegame.player_nations]
        nation_colors = [str(NationSavegameData.query.filter_by(nation_tag = tag, \
                savegame_id = savegame.id).first().color) for tag in nation_tags]

        data = {}

        data["SPA"] = [2,0,0,0,0,0,0,0,0]
        data["FRA"] = [2,0,0,0,0,0,0,0,0]
        data["GBR"] = [2,-1,0,2,3,2,0,0,0]
        data["NED"] = [2,1,0,0,0,1,1,3,0]
        data["HAB"] = [2,1,0,0,0,0,3,1,0]
        data["SWE"] = [2,-2,0,0,0,0,0,0,0]
        data["PLC"] = [2,0,0,0,0,0,0,1,0]
        data["TUR"] = [1,-1,2,1,1,2,2,0,0]
        data["RUS"] = [1,2,0,0,1,1,0,1,0]

        for tag in data.keys():
            data[tag].append(sum(data[tag]))

        return render_template("victory_points.html", header_labels = header_labels, nation_info = zip(nation_tags,nation_colors), data = data)

    else:
        flash(f'Noch keine Siegpunkte vergeben.', 'danger')
        return redirect(url_for("main.home"))

@main.route("/latest_stats/<int:mp_id>", methods = ["GET"])
def latest_stats(mp_id):
    savegames = Savegame.query.filter_by(mp_id = mp_id).order_by(desc(Savegame.year)).all()
    if len(savegames) > 1:
        sg_id1 = savegames[1].id
        sg_id2 = savegames[0].id
        return redirect(url_for("show_stats.parse", sg_id1 = sg_id1, sg_id2 = sg_id2))
    else:
        flash(f'Noch keine Statistik verfügbar.', 'danger')
        return redirect(url_for("main.home"))

@main.route('/colorize.js')
def colorize():
    return render_template('jquery-colorize.js')
