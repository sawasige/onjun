#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
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
				print $cgi->redirect("ontama.cgi?$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("ontama.cgi");
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
				$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂܏����m�F');

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

	my $userid = $cgi->param('userid') || $session->param('userid');

	# ���񂽂܏��擾
	my %ontama = &getOntama($dbh, $userid);
	if ($ontama{'image'}) {
		if ($ontama{'health'}) {
			# �摜 URL
			if ($ontama{'image'} && $tmpl->query(name => 'URL_ONTAMAIMAGE') eq 'VAR') {
				my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
				$tmpl->param(URL_ONTAMAIMAGE => &convertOutput($url));
			}
		} else {
			if ($tmpl->query(name => 'ONTAMADEAD') eq 'VAR') {
				$tmpl->param(ONTAMADEAD => 1);
			}
		}
		
		# ���񂽂܂̖��O
		if ($ontama{'name'} && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontama{'name'}));
		}

		# ������̖��O
		if ($ontama{'ownername'} && $tmpl->query(name => 'ONTAMAOWNERNAME') eq 'VAR') {
			$tmpl->param(ONTAMAOWNERNAME => &convertOutput($ontama{'ownername'}));
		}

		# USERID
		if ($userid != $session->param('userid') && $tmpl->query(name => 'USERID') eq 'VAR') {
			$tmpl->param(USERID => &convertOutput($userid));
		}
		
	} else {
		$msg .= '���񂽂܂͂��܂���B';
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
	my $userid = $cgi->param('userid') || $session->param('userid');

	if ($session->param('powerlevel') < 5 && $userid != $session->param('userid')) {
		$msg .= '���l�̂��񂽂܂͏����ł��܂���B';
		return 0;
	}

	# �f�[�^�`�F�b�N
	if (!$userid) {
		$msg .= '�p�����[�^���s���ł��B';
		return 0;
	}

	my $sql = 'SELECT image FROM ontamausers WHERE userid=?';
	my $image = &selectFetch($dbh, $sql, ($userid));

	# �摜�t�@�C���폜
	unlink($config{'ontamaimagesdir'}.'/'.$image);
	
	# DB �o�^
	&doDB($dbh, 'DELETE FROM ontamausers WHERE userid=?', $userid);
	&doDB($dbh, 'DELETE FROM ontamastatus WHERE userid=?', $userid);
	&doDB($dbh, 'DELETE FROM ontamalogs WHERE userid=?', $userid);

	$msg .= '���񂽂܂��������܂����B';
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

