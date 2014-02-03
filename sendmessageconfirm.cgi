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
				print $cgi->redirect("sendmessage.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("sendmessage.cgi?cancel=1");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &sendMessage();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '���b�Z�[�W���M�m�F', $session->param('receiver_userid') + 0);

				&disp;
			}

			# DB �N���[�Y
			&disconnectDB($dbh);
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
		my $replyid = $session->param('replyid');
		my $receiver_userid = $session->param('receiver_userid');
		my $receiver_name= $session->param('receiver_name');
		my $subject = $session->param('subject');
		my $body = $session->param('body');

		if ($receiver_userid) {
			# �ԐMID
			if ($tmpl->query(name => 'REPLYID') eq 'VAR') {
				$tmpl->param(REPLYID => &convertOutput($replyid));
			}

			# ����ID
			if ($tmpl->query(name => 'RECEIVER_USERID') eq 'VAR') {
				$tmpl->param(RECEIVER_USERID => &convertOutput($receiver_userid));
			}
			# ���於�O
			if ($tmpl->query(name => 'RECEIVER_NAME') eq 'VAR') {
				$tmpl->param(RECEIVER_NAME => &convertOutput($receiver_name));
			}
			# �T�u�W�F�N�g
			if ($tmpl->query(name => 'SUBJECT') eq 'VAR') {
				$tmpl->param(SUBJECT => &convertOutput($subject));
			}
			# �{��
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
			}

		} else {
			$msg .= '���b�Z�[�W�̏�񂪎����܂����B';
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
sub sendMessage() {
	my $userid = $session->param('userid');
	my $replyid = $session->param('replyid');
	my $receiver_userid = $session->param('receiver_userid');
	my $receiver_name;
	my $subject = $session->param('subject');
	my $body = $session->param('body');
	my $mailmessageflag;
	my $mailaddress;

	# �f�[�^�`�F�b�N
	if ($receiver_userid) {
		my @bind = ($receiver_userid, 0);
		my ($name, $address, $flag) = &selectFetchArray($dbh, 'SELECT name, mail, mailmessageflag FROM users WHERE userid=? AND deleteflag=?', @bind);
		$receiver_name = $name;
		$mailaddress = $address;
		$mailmessageflag = $flag;
		if (!$receiver_name) {
			$msg .= '���悪�s���ł��B';
			return 0;
		}
	} else {
		$msg .= '���b�Z�[�W�̏�񂪎����܂����B';
		return 0;
	}

	# �d���`�F�b�N
	my @bind = ($userid, $receiver_userid, $subject, $body);
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=? AND receiver_userid=? AND subject=? AND body=? AND DATE_ADD(sendtime, INTERVAL 5 MINUTE) * 60 > now()', @bind);
	if ($count) {
		$msg .= '�������b�Z�[�W�𑱂��đ��M�ł��܂���B';
		return 0;
	}

	# DB �o�^
	my @bind = ($replyid, $userid, $receiver_userid, $subject, $body);
	my $sql = 
		'INSERT INTO messages('.
		'replyid, '.
		'sender_userid, '.
		'receiver_userid, '.
		'subject, '.
		'body, '.
		'sendtime '.
		') VALUES (?, ?, ?, ?, ?, now())';

	&doDB($dbh, $sql, @bind);

	$msg .= $receiver_name.'���񈶂Ƀ��b�Z�[�W�𑗐M���܂����B';
	$session->clear(['replyid', 'receiver_userid', 'receiver_name', 'subject', 'body']);
	$session->param('msg', $msg);
	$session->flush();

	# ���[�����M
	if ($mailmessageflag) {
		my @bind = ($userid, 0);
		my $sender_name = &selectFetch($dbh, 'SELECT name FROM users WHERE userid=? AND deleteflag=?', @bind);
		my $sub = '�y'.$config{'title'}.'�z'.$sender_name.'���񂩂烁�b�Z�[�W���͂��Ă��܂�';
		my $body =  <<END;
$receiver_name ����A����ɂ��́B
$config{'title'} ����̂��m�点�ł��B

$receiver_name ���񈶂� $sender_name ���񂩂烁�b�Z�[�W���͂��Ă��܂��B

���b�Z�[�W�̓��e���m�F����ɂ͈ȉ��� URL ���N���b�N���Ă��������B

$config{'receivemessagelist_url'}

�����̃��[���ɂ͕ԐM�ł��܂���B
END
		&sendMail($config{'adminmail'}, $mailaddress, $sub, $body, $config{'title'}, $receiver_name);
	}

	# �W�v
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' messagecount=messagecount+1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	} else {
		my $sql = 
			'INSERT addup ('.
			' userid,'.
			' messagecount,'.
			' topiccount,'.
			' topiccommentcount'.
			') VALUES (?, ?, ?, ?)';
		my @bind = ($userid, 1, 0, 0);
		&doDB($dbh, $sql, @bind);
	}

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("sendmessagelist.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('sendmessagelist.cgi');
	}

	return 1;
}

