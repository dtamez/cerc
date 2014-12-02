# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Family'
        db.create_table('family', (
            ('family_name', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True)),
            ('emergency_number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('emergency_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('emergency_relationship', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('address', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cerc.Address'], unique=True)),
            ('father', self.gf('django.db.models.fields.related.OneToOneField')(related_name='father', unique=True, to=orm['cerc.ContactInfo'])),
            ('fee_paid_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('mother', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mother', unique=True, to=orm['cerc.ContactInfo'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cerc', ['Family'])

        # Adding model 'Address'
        db.create_table('address', (
            ('city', self.gf('django.db.models.fields.CharField')(default='Rowlett', max_length=60)),
            ('state', self.gf('localflavor.us.models.USStateField')(default='TX')),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(default='75089', max_length=5)),
        ))
        db.send_create_signal('cerc', ['Address'])

        # Adding model 'ContactInfo'
        db.create_table('contact_info', (
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('email_secondary', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone_secondary', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('cerc', ['ContactInfo'])

        # Adding model 'Teacher'
        db.create_table('teacher', (
            ('contact_info', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.ContactInfo'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Address'])),
        ))
        db.send_create_signal('cerc', ['Teacher'])

        # Adding model 'Student'
        db.create_table('student', (
            ('birthdate', self.gf('django.db.models.fields.DateField')()),
            ('family', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Family'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.OneToOneField')(related_name='student', unique=True, to=orm['cerc.ContactInfo'])),
            ('special_needs', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('cerc', ['Student'])

        # Adding model 'Enrollment'
        db.create_table('enrollment', (
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Course'])),
            ('drop_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Student'])),
            ('entroll_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('cerc', ['Enrollment'])

        # Adding model 'Course'
        db.create_table('course', (
            ('grade_level', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('homework_hours', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('materials_list', self.gf('django.db.models.fields.TextField')()),
            ('age_level', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('length', self.gf('django.db.models.fields.DecimalField')(max_digits=2, decimal_places=1)),
            ('max_slots', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('tuition', self.gf('django.db.models.fields.IntegerField')()),
            ('materials_fee', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('cerc', ['Course'])

        # Adding M2M table for field teachers on 'Course'
        db.create_table('course_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['cerc.course'], null=False)),
            ('teacher', models.ForeignKey(orm['cerc.teacher'], null=False))
        ))
        db.create_unique('course_teachers', ['course_id', 'teacher_id'])

        # Adding model 'Attendance'
        db.create_table('attendance', (
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Course'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Student'])),
        ))
        db.send_create_signal('cerc', ['Attendance'])


    def backwards(self, orm):

        # Deleting model 'Family'
        db.delete_table('family')

        # Deleting model 'Address'
        db.delete_table('address')

        # Deleting model 'ContactInfo'
        db.delete_table('contact_info')

        # Deleting model 'Teacher'
        db.delete_table('teacher')

        # Deleting model 'Student'
        db.delete_table('student')

        # Deleting model 'Enrollment'
        db.delete_table('enrollment')

        # Deleting model 'Course'
        db.delete_table('course')

        # Removing M2M table for field teachers on 'Course'
        db.delete_table('course_teachers')

        # Deleting model 'Attendance'
        db.delete_table('attendance')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'cerc.address': {
            'Meta': {'object_name': 'Address', 'db_table': "'address'"},
            'city': ('django.db.models.fields.CharField', [], {'default': "'Rowlett'", 'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'default': "'TX'"}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "'75089'", 'max_length': '5'})
        },
        'cerc.attendance': {
            'Meta': {'object_name': 'Attendance', 'db_table': "'attendance'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Course']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Student']"})
        },
        'cerc.contactinfo': {
            'Meta': {'object_name': 'ContactInfo', 'db_table': "'contact_info'"},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_secondary': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'phone_secondary': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'cerc.course': {
            'Meta': {'object_name': 'Course', 'db_table': "'course'"},
            'age_level': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grade_level': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'homework_hours': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'max_digits': '2', 'decimal_places': '1'}),
            'materials_fee': ('django.db.models.fields.IntegerField', [], {}),
            'materials_list': ('django.db.models.fields.TextField', [], {}),
            'max_slots': ('django.db.models.fields.IntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cerc.Student']", 'through': "'Enrollment'"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cerc.Teacher']"}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tuition': ('django.db.models.fields.IntegerField', [], {})
        },
        'cerc.enrollment': {
            'Meta': {'object_name': 'Enrollment', 'db_table': "'enrollment'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Course']"}),
            'drop_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'entroll_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Student']"})
        },
        'cerc.family': {
            'Meta': {'object_name': 'Family', 'db_table': "'family'"},
            'address': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cerc.Address']", 'unique': 'True'}),
            'emergency_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'emergency_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'emergency_relationship': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'}),
            'father': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'father'", 'unique': 'True', 'to': "orm['cerc.ContactInfo']"}),
            'fee_paid_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mother': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mother'", 'unique': 'True', 'to': "orm['cerc.ContactInfo']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'cerc.student': {
            'Meta': {'object_name': 'Student', 'db_table': "'student'"},
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'family': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Family']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'special_needs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'student'", 'unique': 'True', 'to': "orm['cerc.ContactInfo']"})
        },
        'cerc.teacher': {
            'Meta': {'object_name': 'Teacher', 'db_table': "'teacher'"},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Address']"}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.ContactInfo']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cerc']
