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
				print $cgi->redirect("option.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("option.cgi?cancel=1");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &registOption();
			}
			
			# DB �N���[�Y
			&disconnectDB($dbh);

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�I�v�V�����m�F');

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
		my $mailmessageflag = $session->param('mailmessageflag');

		if ($mailmessageflag eq '1' && $tmpl->query(name => 'MAILMESSAGEFLAG') eq 'VAR') {
			$tmpl->param(MAILMESSAGEFLAG => $mailmessageflag);
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
sub registOption() {
	my $mailmessageflag = $session->param('mailmessageflag');

	# �f�[�^�`�F�b�N
	if ($mailmessageflag ne '0' && $mailmessageflag ne '1') {
		$msg .= '���b�Z�[�W���m�点���[���̒l���s���ł��B';
		return 0;
	}

	# DB �o�^
	my @bind = ($mailmessageflag, $session->param('userid'));
	my $sql = 
		'UPDATE users SET '.
		'mailmessageflag = ? '.
		'where userid = ?';

	&doDB($dbh, $sql, @bind);

	$msg .= '�ݒ��ύX���܂����B';
	$session->clear(['mailmessageflag']);
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

