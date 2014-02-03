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


#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;
	$msg = '';

$cgi = new CGI;
my $cginame = $cgi->url(-relative=>1); # �� ���̍s���󕶎��ɂȂ��Ă��܂�
my $tmpl = "hoge/$cginame.tmpl";
print $cgi->header(-charset=>'Shift_JIS');
print "$cginame\n";
print "$tmpl\n";

	# �ݒ�ǂݍ���
	%config = &config;

	# �Z�b�V�����擾
	my $check = 0;
	$session = &readSession;
	if (defined $session) {
		$sid = $session->id();
		$session->clear(['openurl']);
		$session->flush();
		# ���O�C�����Ă���Ȃ�z�[���ֈړ�
		if ($session->param('userid')) {
			if (&isMobile()) {
				print $cgi->redirect("home.cgi?$config{'sessionname'}=$sid");
			} else {
				print $cgi->redirect('home.cgi');
			}
			$check = 1;
		}
	}

	if (!$check) {
		$dbh = &connectDB(1);

		# ���݂̉��
		$msg .= &checkOnline($dbh, 0, '�g�b�v�y�[�W');

		# ��ʕ\��
		&disp;

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

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	if (&isMobile) {
		print $cgi->header(-charset=>'Shift_JIS');
	} else {
		print $cgi->header(
			-charset=>'Shift_JIS',
			-cookie=>$cgi->cookie(-path=>$config{'cookie_path'}, -name=>$config{'sessionname'}, -value=>$session->id));
	}
	print $tmpl->output;

	# 1/10 �̊m���ŃZ�b�V�����폜
	if (int(rand(10)) == 1) {
		&deleteOldSession();
	}
}

#################
# �Z�b�V�����폜
sub deleteOldSession {
	my @files = glob($config{'sessiondir'}.'/*');
	foreach my $file(@files) {
		my $lastmodified = (stat $file)[9];
		# 1���Ԍo�߂����t�@�C���͍폜
		if ($lastmodified < time() - 60 * 60 * 24 * 1) {
			unlink($file);
		}
	}
}
