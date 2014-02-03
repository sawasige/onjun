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
my $forumid = 0;
my $forumname = '';
my $forumnote = '';
my $topicid = 0;
my $topictitle = '';
my $topicbody = '';

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
			$topicid = $cgi->param('topicid');
			# ��ʃ��_�C���N�g
			if (&isMobile()) {
				# �Z�b�V������ URL ���ߍ���
				print $cgi->redirect("topic.cgi?topicid=$topicid&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("topic.cgi?topicid=$topicid");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �g�s�b�N���擾
			&getTopicInfo();

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &deleteTopic();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�폜�m�F');

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
		my $title = $session->param('title');
		my $body = $session->param('body');

		if ($forumname) {
			# �t�H�[����ID
			if ($forumname && $tmpl->query(name => ['FORUMID']) eq 'VAR') {
				$tmpl->param(FORUMID => &convertOutput($forumid));
			}
			# �t�H�[����URL
			if ($tmpl->query(name => ['FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?forumid='.$forumid;
				if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(FORUMURL => &convertOutput($url));
			}
			# �t�H�[������
			if ($forumname && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
				$tmpl->param(FORUMNAME => &convertOutput($forumname));
			}
			# �t�H�[��������
			if ($forumnote && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
				$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
			}
			# �g�s�b�NID
			if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
				$tmpl->param(TOPICID => $topicid);
			}
			# �g�s�b�NURL
			if ($tmpl->query(name => ['TOPICURL']) eq 'VAR') {
				my $url = 'topic.cgi?topicid='.$topicid;
				if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(TOPICURL => &convertOutput($url));
			}
			# �g�s�b�N�^�C�g��
			if ($tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($topictitle));
			}
			# �g�s�b�N�{��
			if ($tmpl->query(name => ['BODY']) eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($topicbody, 1));
			}

			# �Y�t�t�@�C��1
			if ($tmpl->query(name => ['FILE1LARGEURL']) eq 'VAR') {
				my $lname1 = &getPublishFile('tp'.$topicid.'_1');
				if ($lname1) {
					$tmpl->param(FILE1LARGEURL => $lname1);
					if ($tmpl->query(name => ['FILE1SMALLURL']) eq 'VAR') {
						my $sname1 = &getPublishFile('tp'.$topicid.'_1_s');
						if ($sname1) {
							$tmpl->param(FILE1SMALLURL => $sname1);
						}
					}
				}
			}

			# �Y�t�t�@�C��2
			if ($tmpl->query(name => ['FILE2LARGEURL']) eq 'VAR') {
				my $lname2 = &getPublishFile('tp'.$topicid.'_2');
				if ($lname2) {
					$tmpl->param(FILE2LARGEURL => $lname2);
					if ($tmpl->query(name => ['FILE2SMALLURL']) eq 'VAR') {
						my $sname2 = &getPublishFile('tp'.$topicid.'_2_s');
						if ($sname2) {
							$tmpl->param(FILE2SMALLURL => $sname2);
						}
					}
				}
			}

			# �Y�t�t�@�C��3
			if ($tmpl->query(name => ['FILE3LARGEURL']) eq 'VAR') {
				my $lname3 = &getPublishFile('tp'.$topicid.'_3');
				if ($lname3) {
					$tmpl->param(FILE3LARGEURL => $lname3);
					if ($tmpl->query(name => ['FILE3SMALLURL']) eq 'VAR') {
						my $sname3 = &getPublishFile('tp'.$topicid.'_3_s');
						if ($sname3) {
							$tmpl->param(FILE3SMALLURL => $sname3);
						}
					}
				}
			}

		} else {
			$msg .= '�g�s�b�N�̏�񂪎����܂����B';
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => &convertOutput($msg));
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

####################
# �g�s�b�N���擾
sub getTopicInfo() {
	# �g�s�b�NID
	$topicid = $cgi->param('topicid');

	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.title, b.body'.
		' FROM forums a, topics b'.
		' WHERE a.forumid=b.forumid AND b.topicid=? AND a.deleteflag=? AND b.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topicid, '0', '0', $session->param('powerlevel'));
	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND b.registuserid=?';
		push(@bind, $session->param('userid'));
	}
	my ($fid, $fname, $fnote, $ttitle, $tbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	if (!$forumname) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}

###############
# �g�s�b�N�폜
sub deleteTopic() {
	if ($msg) {
		return 0;
	}

	my $userid = $session->param('userid');

	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topicid, $userid, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE topicid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= '�p�����[�^���s���ł��B';
			return 0;
		}
	} else {
		$userid = &selectFetch($dbh, 'SELECT registuserid FROM topics WHERE topicid=? AND deleteflag=?', ($topicid, '0'));
	}

	# DB �o�^
	my @bind = ('1', $topicid);
	my $sql = 'UPDATE topics SET deleteflag=? WHERE topicid=?';
	&doDB($dbh, $sql, @bind);

	# �t�@�C���폜
	&hideFile('tp'.$topicid);

	# �W�v
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccount=topiccount-1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	}

	# �g�s�b�N�R�����g���폜
	$sql = 'SELECT topiccommentid, registuserid FROM topiccomments WHERE topicid=? AND deleteflag=?';
	my @comments = &selectFetchArrayRef($dbh, $sql, ($topicid, '0'));
	foreach my $row(@comments) {
		my ($topiccommentid, $registuserid) = @$row;
		# �t�@�C���폜
		&hideFile('tc'.$topiccommentid);

		# �W�v
		if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $registuserid)) {
			my $sql = 
				'UPDATE addup SET'.
				' topiccommentcount=topiccommentcount-1'.
				' WHERE'.
				' userid=?';
			my @bind = ($registuserid);
			&doDB($dbh, $sql, @bind);
		}
	}
	$sql = 'UPDATE topiccomments SET deleteflag=? WHERE topicid=?';
	@bind = ('1', $topicid);
	&doDB($dbh, $sql, @bind);

	$msg .= '�g�s�b�N���폜���܂����B';
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("forum.cgi?forumid=$forumid&$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('forum.cgi?forumid='.$forumid);
	}

	return 1;
}

