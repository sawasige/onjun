#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
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

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �o�^
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkValue();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂܂̊J�n');

			&disp;
		}

		# DB �N���[�Y
		&disconnectDB($dbh);
	}
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	my $ontamaname = '';
	if ($cgi->param('cancel')) {
		$ontamaname = $session->param('ontamaname');
	} elsif ($cgi->param('submit')) {
		$ontamaname = $cgi->param('ontamaname');
	}
	
	if ($ontamaname && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
		$tmpl->param(ONTAMANAME => &convertOutput($ontamaname));
	}

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


###############
# ���̓`�F�b�N
sub checkValue() {
	if ($msg) {
		return 0;
	}

	# ���b�Z�[�W���m�点���[��
	my $ontamaname = $cgi->param('ontamaname');
	$msg .= &checkString('���񂽂܂̖��O', $ontamaname, 30, 1);
	if ($msg) {
		return 0;
	}

	# ���̓`�F�b�N�����I�I
	$session->param('ontamaname', $ontamaname);
	$session->flush();
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect('setontamaconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# �Z�b�V������ Cookie ���ߍ���
		print $cgi->redirect('setontamaconfirm.cgi');
	}

	return 1;
}

