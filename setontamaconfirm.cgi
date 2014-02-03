#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
use File::Copy;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my @ages = ();

#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;
	$msg = '';

	# �ݒ�ǂݍ���
	%config = &config;

	# �Z�b�V�����ǂݍ���
	$session = &readSession(1);
	if (defined $session) {
		# �Z�b�V���� ID
		$sid = $session->id;
		
		# �L�����Z���Ȃ�߂�
		if ($cgi->param('cancel')) {
			# ��ʃ��_�C���N�g
			if (&isMobile()) {
				# �Z�b�V������ URL ���ߍ���
				print $cgi->redirect("setontama.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("setontama.cgi?cancel=1");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &registValue();
			}
			
			# DB �N���[�Y
			&disconnectDB($dbh);

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂܊J�n�m�F');

				&disp;
			}
		}
	}
	
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	if (!$msg) {
		my $ontamaname = $session->param('ontamaname');

		if ($ontamaname && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontamaname));
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#################
# ���b�Z�[�W���M
sub registValue() {
	my $ontamaname = $session->param('ontamaname');

	# �f�[�^�`�F�b�N
	if (!$ontamaname) {
		$msg .= '�p�����[�^���s���ł��B';
		return 0;
	}

	my $sql = 'SELECT ontamaid, image FROM ontama WHERE parentid=?';
	my @ontamalist = &selectFetchArrayRef($dbh, $sql, (0));
	my $idx = int(rand(@ontamalist + 0));
	my $ontama = $ontamalist[$idx];
	my ($ontamaid, $sourceimage) = @$ontama;

	# �摜�t�@�C����
	my $destimage = $session->param('userid').'_'.&getRandomString(3).'.gif';

	# �摜�t�@�C���R�s�[
	copy($config{'ontamadir'}.'/'.$sourceimage, $config{'ontamaimagesdir'}.'/'.$destimage);
	
	# DB �o�^
	my @bind = ($session->param('userid'), $ontamaid, $ontamaname, $destimage, 1, 1, 0, 50, 50, 50);
	my $sql =  'INSERT INTO ontamausers(userid, ontamaid, name, image, days, level, grow, health, hungry, happy, growdate, registtime, lasttime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW(), NOW(), NOW())';
	&doDB($dbh, $sql, @bind);

	$msg .= '���񂽂܂̂��܂��̗p�ӂ��ł��܂����B�������y���݂ɂ��Ă��Ă��������I';
	$session->clear(['ontamaname']);
	$session->param('msg', $msg);
	$session->flush();

	
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("ontama.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('ontama.cgi');
	}

	return 1;
}

