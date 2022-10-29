from io import BytesIO
from flask import ( 
    Flask, render_template,url_for, request,send_file,
    redirect, flash, session,abort
)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "mnbearpig_NUMDAN888/Hg"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(
 #   app.root_path,'hawis.db'
#)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hawis.db'

# Suppress deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


    
class Activity(db.Model):
    id        = db.Column(db.Integer(), primary_key = True)
    name      = db.Column(db.String(120), nullable = False, unique = True)
    persons   = db.relationship('Person', lazy='select', cascade="all, delete")
    def __rep__(self):
        return f'Activity(name = {ame})'  
      
class Person(db.Model):
    id           = db.Column(db.Integer(), primary_key = True)
    name         = db.Column(db.String(60), nullable = False, unique = False)
    phone        = db.Column(db.String(20), nullable = False, unique = True)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    wilaya       = db.Column(db.String(20), nullable = False)
    zone         = db.Column(db.String(60))
    show_me      = db.Column(db.Boolean(), default = False)
    vip          = db.Column(db.Boolean(), default = False)
    #======================== Auther info ===============================
    #email        = db.Column(db.String(50), unique = True)
    #address      = db.Column(db.String(60), default = 0)
    #description  = db.Column(db.Text)
    #======================== save image ===============================
    image_file   = db.Column(db.String(250), default = 0)
    image_data   = db.Column(db.LargeBinary)
    #=======================================================
    #status       = db.Column(db.String(10), nullable = False) # Status : 1 : free , 2 : Standard , 3 : Pro 
    #========================================================
    activity     = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
   
    #def __rep__(self):
     #   return f'Person {self.name}'
    
    def to_dict(self):
        return {
            'name':self.name,
            'phone':self.phone,
            'wilaya':self.wilaya,
            'zone':self.zone,
        }
    
class Project(db.Model):
    id           = db.Column(db.Integer(), primary_key = True)
    title        = db.Column(db.String(255), nullable = False, unique = True)
    description  = db.Column(db.Text)
    image        = db.Column(db.String(200), default = 0)
    date_added   = db.Column(db.DateTime, default = datetime.utcnow)
    show_me      = db.Column(db.Boolean(), default = True)
    person       = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
   
    def __rep__(self):
        return f'Project {self.title}'
    
db.create_all()


@app.route('/',methods=['GET','POST'], defaults={"page":1}) 
@app.route('/<int:page>',methods=['GET','POST'])
def index(page):
    page = page
    pages = 3
    #flash("You are in Index page ")
    session.clear()
    activities  = Activity.query.order_by(Activity.name).all() 
    #persons     = Person.query.order_by(Person.date_created).all()
    persons_vip = Person.query.filter(Person.show_me == True, Person.vip == True ).all()
    persons     = Person.query.filter(Person.show_me == True ).paginate(page,pages,error_out=False)
    return render_template("index.html",
                            title      = "Hawis - Accueil",
                            activities = activities,
                            persons_vip= persons_vip,
                            persons    = persons
                            )  
    
@app.route('/configuration',methods=['GET','POST'], defaults={"page":1}) 
@app.route('/configuration/<int:page>',methods=['GET','POST'])
def configuration(page):
    page = page
    pages = 3
    flash("Configuration ... ")   
    session.clear()
    activities = Activity.query.order_by(Activity.name).all()
    persons    = Person.query.paginate(page,pages,error_out=False)#.order_by(Person.show_me)
    return render_template("configuration.html",
                            title   = "Hawis - Configuration..",
                            activities = activities,
                            persons = persons
                            )
    


   
@app.route('/person_search', methods = ['GET', 'POST'], defaults={"page":1}) 
def person_search(page):
    #flash("You are in Index page ")
    
    page = page
    pages = 3
    
    if request.method == 'POST':
        activity_search = request.form.get('activity_search')
        wilaya_search = request.form.get('wilaya_search')
        
        activities  = Activity.query.order_by(Activity.name).all()
        persons_vip = Person.query.filter(Person.show_me == True, Person.vip == True ).all()
        if activity_search:
            if wilaya_search:
                persons = Person.query.filter( Person.show_me == True , Person.activity == activity_search, Person.wilaya == wilaya_search ).paginate(page,pages,error_out=False)
            else:
                
                persons = Person.query.filter( Person.show_me == True , Person.activity == activity_search).paginate(page,pages,error_out=False)    
        else:
            if wilaya_search:
                persons = Person.query.filter( Person.show_me == True , Person.wilaya == wilaya_search ).paginate(page,pages,error_out=False)    
            else:
                persons = Person.query.filter(Person.show_me == True).paginate(page,pages,error_out=False)      #persons     = Person.query.order_by(Person.date_created).all()
           
    return render_template("index.html",
                            title      = "Hawis - search",
                            activities = activities,
                            persons    = persons,
                            persons_vip= persons_vip
                            )     
   
    
@app.route('/name_search', methods=['GET','POST'], defaults={"page":1})
def name_search(page):
    page = page
    pages = 3
    
    activities  = Activity.query.order_by(Activity.name).all()
    persons_vip = Person.query.filter(Person.show_me == True, Person.vip == True ).all()
    if request.method == 'POST':
        name_search = request.form.get('name_search')
        if name_search:
            persons = Person.query.filter(Person.name.contains(name_search)).paginate(page,pages,error_out=False) 
            #persons = Person.query.filter(Person.name == name_search).all()
        else:
            persons = Person.query.filter(Person.show_me == True).paginate(page,pages,error_out=False) 
    return render_template("index.html",
                            title      = "Hawis - name search",
                            activities = activities,
                            persons    = persons,
                            persons_vip= persons_vip
                            )  

    
@app.route('/name_search_config', methods=['GET','POST'], defaults={"page":1})
def name_search_config(page):
    page = page
    pages = 3
    
    activities  = Activity.query.order_by(Activity.name).all()
    if request.method == 'POST':
        name_search = request.form.get('name_search_config')
        persons = Person.query.filter(Person.name.contains(name_search)).paginate(page,pages,error_out=False) 
    return render_template("configuration.html",
                            title      = "Hawis - name search",
                            activities = activities,
                            persons    = persons
                            )  


  
@app.route('/person_register') 
def person_register():
    #flash("SignUp ... ")   
    activities  = Activity.query.order_by(Activity.name).all()
    return render_template("person/register.html",
                            title   = "Hawis - S'inscrire",
                            activities = activities
                            )      
def save_images(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_PATH'],filename))  
    return filename 

app.config['UPLOAD_PATH'] = 'static/img/persons'

@app.route('/person_add',methods=['POST','GET']) 
def person_add():
    #flash("You are in Index page ")
    if request.method == 'POST':
        session.clear()   
        # Check if name is blank
        if not len(request.form['name'])>0:
            flash('Name is required')
            return redirect('/')
        # Check if phone is blank
        if not len(request.form['phone'])>0:
            flash('phone is required')
            return redirect('/')
        activity    = request.form['activity']
        name        = request.form['name']
        phone       = request.form['phone']
        wilaya      = request.form['wilaya']
        zone        = request.form['zone']                 
        #status      = request.form['status']
        #email       = request.form['email']
        #address     = request.form['address']
        #description = request.form['description']              
        new_person = Person(name=name,activity=activity, phone=phone, wilaya=wilaya, 
                            zone=zone, image_file=save_images(request.files['image_file']) ,
                            image_data=request.files['image_file'].read())               
        try:
            db.session.add(new_person)
            db.session.commit()
            flash('Félécitation vous avez enregistré avec succé.')
        except:
            flash('There was an issue adding your person.')
        return redirect('/')
   
@app.route('/person_update/<int:id>',methods=['POST','GET'])
def person_update(id):
    person = Person.query.get_or_404(id)
    #flash(f'Hello {person.name} you are updating ')
    if request.form.get('show_checkbox') == 'on':
        show = True
    else:
        show = False
    if request.form.get('vip_checkbox') == 'on':
        vip = True
    else:
        vip = False    
    if request.method == 'POST':
        if request.files['image_file']:
            try:
                os.unlink(os.path.join(current_app.root_path,app.config['UPLOAD_PATH']
                + person.image_file))
                person.image_file = save_images(request.files['image_file'])
                person.image_data=request.files['image_file'].read()
            except:
                person.image_file = save_images(request.files['image_file'])
                person.image_data=request.files['image_file'].read()
                
        person.activity = request.form['activity']
        person.name     = request.form['name']
        person.phone    = request.form['phone']
        person.wilaya   = request.form['wilaya']
        person.zone     = request.form['zone']
        person.show_me  = show
        person.vip      = vip
        try:
            db.session.commit()
            flash('person update','success')
            return redirect(url_for('configuration'))
        except:
            return 'There was an issue updating your informations...'  
    activities  = Activity.query.order_by(Activity.name).all()
    return render_template('person/update.html',person = person,activities = activities)
  
@app.route('/person_delete/<id>')
def person_delete(id):
    person = Person.query.get_or_404(id)
    try:
        os.unlink(os.path.join(current_app.root_path,app.config['UPLOAD_PATH']
                + person.image_file))
        db.session.delete(person)
    except: 
        db.session.delete(person)   
    db.session.commit()
    flash(f'{person.name} has deleted','success')
    return redirect(url_for('configuration'))
                   
@app.route('/activity_add',methods=['POST','GET']) 
def Activity_add():
    #flash("You are in Activities list")
    if request.method == 'POST':
        new_activity = Activity(name = request.form['activity'])
        try:
            db.session.add(new_activity)
            db.session.commit()
            return redirect('/configuration')
        except:
            return 'There was an issue adding your Activity.'
    else:    
        activities = Activity.query.order_by(Activity.name).all()
        return render_template("configuration.html",
                                title      = "List of Activities",
                                activities = activities
                                )
@app.route('/activity_update/<int:id>',methods=['POST','GET'])
def activity_update(id):
    
    activity = Activity.query.get_or_404(id)
    #flash(f'Hello {person.name} you are updating ')
    if request.method == 'POST':
        activity.name = request.form['activity']
        try:
            db.session.commit()
            return redirect('/configuration')
        except:
            return 'There was an issue updating the activity...'  
    else:
        return render_template('activity_update.html',
                                title    = "Updating activity",
                                activity = activity         
                              )

@app.route('/activity_delete/<int:id>')
def activity_delete(id):
    activity_to_delete = Activity.query.get_or_404(id)
    try:
        db.session.delete(activity_to_delete)
        db.session.commit()
        return redirect('/configuration')
        
    except:
        return 'There was an problem deleting this activity !'
    





#if __name__ == "__main__":
 #   app.run(debug=True, host='127.0.0.1', port=5000)
    
    
