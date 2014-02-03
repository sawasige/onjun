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
my %message = ();

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

		# ���b�Z�[�W�擾
		&getMessage();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '��M���b�Z�[�W');

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

	if ($message{'subject'}) {
		# ���M��
		if ($tmpl->query(name => 'SENDER') eq 'VAR') {
			$tmpl->param(SENDER => &convertOutput($message{'sender_name'}));
		}
		# ���M��URL
		if ($tmpl->query(name => 'SENDERURL') eq 'VAR') {
			my $url = 'profile.cgi?userid='.$message{'sender_userid'};
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(SENDERURL => &convertOutput($url));
		}
		# ���M����
		if ($tmpl->query(name => 'SENDTIME') eq 'VAR') {
			$tmpl->param(SENDTIME => &convertOutput($message{'sendtime'}));
		}
		# �T�u�W�F�N�g
		if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
			$tmpl->param(SUBJECT => &convertOutput($message{'subject'}));
		}
		# �{��
		if ($tmpl->query(name => 'BODY') eq 'VAR') {
			$tmpl->param(BODY => &convertOutput($message{'body'}, 1));
		}
		# �ԐM URL
		if ($tmpl->query(name => 'URL_REPLYMESSAGE') eq 'VAR') {
			my $url = 'sendmessage.cgi?replyid='.$cgi->param('messageid');
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			$tmpl->param(URL_REPLYMESSAGE => &convertOutput($url));
		}
		# �폜 URL
		if ($tmpl->query(name => 'URL_RECEIVEMESSAGEDELETE') eq 'VAR') {
			my $url = 'receivemessagedelete.cgi?messageid='.$cgi->param('messageid');
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			$tmpl->param(URL_RECEIVEMESSAGEDELETE => &convertOutput($url));
		}

	} else {
		$msg .= '���b�Z�[�W������܂���B';
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

#################
# ���b�Z�[�W�擾
sub getMessage() {
	my $messageid = $cgi->param('messageid');
	my $opened = 0;
	if ($messageid) {
		my $sql = 'SELECT a.subject, a.body, a.sendtime, a.opentime, b.userid, b.name FROM messages a, users b'.
			' WHERE a.sender_userid=b.userid AND a.messageid=? AND a.receiver_userid=? AND a.receiver_deleteflag=?';
		my @bind = ($messageid, $session->param('userid'), 0);
		my ($subject, $body, $sendtime, $opentime, $sender_userid, $sender_name) = &selectFetchArray($dbh, $sql, @bind);
		$opentime =~ s/[^\d]//g;
		$opentime += 0;
		$opened = $opentime;
		if ($subject) {
			$message{'subject'} = $subject;
			$message{'body'} = $body;
			$message{'sender_userid'} = $sender_userid;
			$message{'sender_name'} = $sender_name;
			$message{'sendtime'} = $sendtime;
		}
	}

	if ($message{'subject'} && !$opened) {
		my @bind = ($messageid, $session->param('userid'));
		my $sql = 'UPDATE messages SET opentime=now() WHERE messageid=? AND receiver_userid=?';
		&doDB($dbh, $sql, @bind);
	}

}

