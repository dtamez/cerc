# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting field 'Course.start_date'
        db.delete_column('course', 'start_date')

        # Deleting field 'Course.end_date'
        db.delete_column('course', 'end_date')

        # Changing field 'Course.semester'
        db.alter_column('course', 'semester_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Semester']))


    def backwards(self, orm):

        # Adding field 'Course.start_date'
        db.add_column('course', 'start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Adding field 'Course.end_date'
        db.add_column('course', 'end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)

        # Changing field 'Course.semester'
        db.alter_column('course', 'semester_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cerc.Semester'], null=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'cerc.address': {
            'Meta': {'ordering': "['street', 'city']", 'object_name': 'Address', 'db_table': "'address'"},
            'city': ('django.db.models.fields.CharField', [], {'default': "'Rowlett'", 'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'default': "'TX'"}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "'75089'", 'max_length': '5'})
        },
        'cerc.attendance': {
            'Meta': {'ordering': "['date', 'course', 'student']", 'object_name': 'Attendance', 'db_table': "'attendance'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Course']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Student']"})
        },
        'cerc.contactinfo': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ContactInfo', 'db_table': "'contact_info'"},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_secondary': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'phone_secondary': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'cerc.course': {
            'Meta': {'ordering': "['title', 'code']", 'object_name': 'Course', 'db_table': "'course'"},
            'age_level': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'days_per_week': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'first_time_choice': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'grade_level': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'homework_hours': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'max_digits': '2', 'decimal_places': '1'}),
            'materials_fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'materials_list': ('django.db.models.fields.TextField', [], {}),
            'max_slots': ('django.db.models.fields.IntegerField', [], {}),
            'min_slots': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'schedule_considerations': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'second_time_choice': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Semester']"}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cerc.Student']", 'null': 'True', 'through': "'Enrollment'", 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cerc.Teacher']"}),
            'third_time_choice': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tuition': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'cerc.enrollment': {
            'Meta': {'ordering': "['course', 'student']", 'object_name': 'Enrollment', 'db_table': "'enrollment'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Course']"}),
            'drop_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'entroll_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Student']"})
        },
        'cerc.family': {
            'Meta': {'ordering': "['family_name']", 'object_name': 'Family', 'db_table': "'family'"},
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
        'cerc.semester': {
            'Meta': {'ordering': "['start_date', 'name']", 'object_name': 'Semester', 'db_table': "'semester'"},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'cerc.student': {
            'Meta': {'ordering': "['student']", 'object_name': 'Student', 'db_table': "'student'"},
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'family': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Family']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'special_needs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'student'", 'unique': 'True', 'to': "orm['cerc.ContactInfo']"})
        },
        'cerc.teacher': {
            'Meta': {'ordering': "['contact_info']", 'object_name': 'Teacher', 'db_table': "'teacher'"},
            'address': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.Address']"}),
            'contact_info': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cerc.ContactInfo']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cerc']
