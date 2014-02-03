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
my $topicid = 0;
my $commentcount = 0;
my @comments = ();
my $start = 0;
my $size = 10;

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
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �R�����g�ꗗ�擾
		&getCommentList();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N');

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

	# ���b�Z�[�W
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	

	# �R�����g������URL
	if ($tmpl->query(name => ['POSTTOPICCOMMENTURL']) eq 'VAR') {
		my $url = 'posttopiccomment.cgi?topicid='.$topicid;
		if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
		}
		$tmpl->param(POSTTOPICCOMMENTURL => &convertOutput($url));
	}


	if ($tmpl->query(name => ['FORUMNAME']) eq 'VAR' || 
		$tmpl->query(name => ['FORUMNOTE']) eq 'VAR' ||
		$tmpl->query(name => ['FORUMURL']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICTITLE']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICBODY']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICREGISTTIME']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICREGISTUSERURL']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICREGISTUSERNAME']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICREGISTUSERURL']) eq 'VAR' ||
		$tmpl->query(name => ['TOPICREGISTUSERURL']) eq 'VAR' ||
		$tmpl->query(name => ['MODIFYTOPICURL']) eq 'VAR' ||
		$tmpl->query(name => ['DELETETOPICURL']) eq 'VAR') {
		my $sql = 
			'SELECT a.forumid, a.name, a.note, b.title, b.body, b.registtime, c.userid, c.name'.
			' FROM forums a, topics b, users c'.
			' WHERE a.forumid=b.forumid AND b.registuserid=c.userid AND a.deleteflag=? AND a.powerlevel<=? AND b.topicid=? AND b.deleteflag=? ';
		my @bind = ('0', $session->param('powerlevel'), $topicid, '0');
		my ($forumid, $name, $note, $title, $body, $registtime, $registuserid, $registusername) = &selectFetchArray($dbh, $sql, @bind);

		# �t�H�[������
		if ($name && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($name));
		}
		# �t�H�[��������
		if ($note && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($note, 1));
		}
		# �t�H�[����URL
		if ($name && $tmpl->query(name => ['FORUMURL']) eq 'VAR') {
			my $url = 'forum.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(FORUMURL => &convertOutput($url));
		}
		# �V�K�g�s�b�N�쐬URL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
		}
		# �g�s�b�NID
		if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
			$tmpl->param(TOPICID => $topicid);
		}
		# �g�s�b�N�^�C�g��
		if ($title && $tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($title));
		}
		# �g�s�b�N�^�C�g��
		if ($title && $tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($title));
		}
		# �g�s�b�N�{��
		if ($body && $tmpl->query(name => ['TOPICBODY']) eq 'VAR') {
			$tmpl->param(TOPICBODY => &convertOutput($body, 1));
		}
		# �o�^����
		if ($registtime && $tmpl->query(name => ['TOPICREGISTTIME']) eq 'VAR') {
			$tmpl->param(TOPICREGISTTIME => $registtime);
		}
		# �o�^��
		if ($registusername && $tmpl->query(name => ['TOPICREGISTUSERNAME']) eq 'VAR') {
			$tmpl->param(TOPICREGISTUSERNAME => &convertOutput($registusername));
		}
		# �o�^��URL
		if ($registuserid && $tmpl->query(name => ['TOPICREGISTUSERURL']) eq 'VAR') {
			my $url = 'profile.cgi?userid='.$registuserid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICREGISTUSERURL => &convertOutput($url));
		}
		# �g�s�b�N�C��URL
		if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['MODIFYTOPICURL']) eq 'VAR') {
			my $url = 'modifytopic.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MODIFYTOPICURL => &convertOutput($url));
		}
		# �g�s�b�N�폜URL
		if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['DELETETOPICURL']) eq 'VAR') {
			my $url = 'deletetopicconfirm.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(DELETETOPICURL => &convertOutput($url));
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
	}

	# �R�����g�ꗗ
	if (@comments && $tmpl->query(name => 'COMMENTS') eq 'LOOP') {
		my @commentvars = ();
		my $commentno = $start + 1;
		foreach my $row(@comments) {
			my ($topiccommentid, $body, $registtime, $registuserid, $registusername) = @$row;
			my %commentvar;
			# �R�����g�A��
			if ($tmpl->query(name => ['COMMENTS', 'COMMENTNO']) eq 'VAR') {
				$commentvar{'COMMENTNO'} = &convertOutput($commentno);
			}
			$commentno++;
			# �R�����gID
			if ($tmpl->query(name => ['COMMENTS', 'ID']) eq 'VAR') {
				$commentvar{'ID'} = &convertOutput($topiccommentid);
			}
			# �R�����g
			if ($tmpl->query(name => ['COMMENTS', 'BODY']) eq 'VAR') {
				$commentvar{'BODY'} = &convertOutput($body, 1);
			}
			# �R�����g�o�^����
			if ($tmpl->query(name => ['COMMENTS', 'REGISTTIME']) eq 'VAR') {
				$commentvar{'REGISTTIME'} = $registtime;
			}
			# �R�����g�o�^��
			if ($tmpl->query(name => ['COMMENTS', 'REGISTUSERNAME']) eq 'VAR') {
				$commentvar{'REGISTUSERNAME'} = &convertOutput($registusername);
			}
			# �R�����g�o�^��URL
			if ($tmpl->query(name => ['COMMENTS', 'REGISTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$registuserid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'REGISTUSERURL'} = &convertOutput($url);
			}
			# �R�����gURL
			if ($tmpl->query(name => ['COMMENTS', 'TOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'topiccomment.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'TOPICCOMMENTURL'} = &convertOutput($url);
			}
			# �R�����g�C��URL
			if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['COMMENTS', 'MODIFYTOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'modifytopiccomment.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'MODIFYTOPICCOMMENTURL'} = &convertOutput($url);
			}
			# �R�����g�C��URL
			if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['COMMENTS', 'DELETETOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'deletetopiccommentconfirm.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'DELETETOPICCOMMENTURL'} = &convertOutput($url);
			}

			my $existfile = 0;
			# �Y�t�t�@�C��1
			if ($tmpl->query(name => ['COMMENTS', 'FILE1LARGEURL']) eq 'VAR') {
				my $lname1 = &getPublishFile('tc'.$topiccommentid.'_1');
				if ($lname1) {
					$existfile++;
					$commentvar{'FILE1LARGEURL'} = $lname1;
					if ($tmpl->query(name => ['COMMENTS', 'FILE1SMALLURL']) eq 'VAR') {
						my $sname1 = &getPublishFile('tc'.$topiccommentid.'_1_s');
						if ($sname1) {
							$commentvar{'FILE1SMALLURL'} = $sname1;
						}
					}
				}
			}
			# �Y�t�t�@�C��2
			if ($tmpl->query(name => ['COMMENTS', 'FILE2LARGEURL']) eq 'VAR') {
				my $lname2 = &getPublishFile('tc'.$topiccommentid.'_2');
				if ($lname2) {
					$existfile++;
					$commentvar{'FILE2LARGEURL'} = $lname2;
					if ($tmpl->query(name => ['COMMENTS', 'FILE2SMALLURL']) eq 'VAR') {
						my $sname2 = &getPublishFile('tc'.$topiccommentid.'_2_s');
						if ($sname2) {
							$commentvar{'FILE2SMALLURL'} = $sname2;
						}
					}
				}
			}
			# �Y�t�t�@�C��3
			if ($tmpl->query(name => ['COMMENTS', 'FILE3LARGEURL']) eq 'VAR') {
				my $lname3 = &getPublishFile('tc'.$topiccommentid.'_3');
				if ($lname3) {
					$existfile++;
					$commentvar{'FILE3LARGEURL'} = $lname3;
					if ($tmpl->query(name => ['COMMENTS', 'FILE3SMALLURL']) eq 'VAR') {
						my $sname3 = &getPublishFile('tc'.$topiccommentid.'_3_s');
						if ($sname3) {
							$commentvar{'FILE3SMALLURL'} = $sname3;
						}
					}
				}
			}
			# �Y�t�t�@�C���̗L��
			if ($existfile && $tmpl->query(name => ['COMMENTS', 'EXISTFILE']) eq 'VAR') {
				$commentvar{'EXISTFILE'} = 1;
			}

			# �g�ђ[��
			if (&isMobile && $tmpl->query(name => ['COMMENTS', 'MOBILE']) eq 'VAR') {
				$commentvar{'MOBILE'} = 1;
			}

			push(@commentvars, \%commentvar);
		}
		$tmpl->param(COMMENTS => \@commentvars);
	}

	# �O�y�[�W
	if ($start > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $prevstart = $start - $size;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		my $url = &getCondUrl();
		$url .= '&start='.$prevstart;
		$url .= '&size='.$size;
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# �O�y�[�W�ԍ�
	if ($start > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
		my $startno = $no - 9;
		if ($startno < 1) {
			$startno = 1;
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = &getCondUrl();
			# �J�n�s
			$url .= '&start='.($i-1) * $size;
			$url .= '&size='.$size;
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGEURL']) eq 'VAR') {
				$page{BACKPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGELABEL']) eq 'VAR') {
				$page{BACKPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
		}
		$tmpl->param(BACKPAGELOOP => \@pagedata);
	}

	# ���y�[�W
	if (($start + @comments) < $commentcount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = &getCondUrl();
		$url .= '&start='.$nextstart;
		$url .= '&size='.$size;
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# ���y�[�W�ԍ�
	if (($start + @comments) < $commentcount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($commentcount / $size);
		if ($commentcount % $size) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = &getCondUrl();
			# �J�n�s
			$url .= '&start='.($i-1) * $size;
			$url .= '&size='.$size;
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
			if (@pagedata >= 9) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# ���݃y�[�W
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		# �y�[�W��������ꍇ�����\��
		if ($size < $commentcount) {
			my $no = int($start / $size) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# ���������� URL �G���R�[�h
sub getCondUrl {
	my $url = $cgi->url(-relative=>1).'?';
	$url .= 'topicid='.$topicid;
	# �Z�b�V����
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	return $url;
}

#####################
# �R�����g�ꗗ�擾
sub getCommentList() {
	$commentcount = 0;
	@comments = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# �R�����g���w�肳��Ă���ꍇ�� topicid ��T��
	if ($cgi->param('topiccommentid')) {
		my $sql = 
			' SELECT a.topicid , count(a.topicid)'.
			' FROM'.
			' topiccomments a, topiccomments b'.
			' WHERE'.
			' a.topicid=b.topicid'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?'.
			' AND b.topiccommentid=?'.
			' AND a.registtime <= b.registtime'.
			' GROUP BY a.topicid';
		my @bind = ('0', '0', $cgi->param('topiccommentid'));
		my ($tid, $ccount) = &selectFetchArray($dbh, $sql, @bind);
		if ($tid) {
			$topicid = $tid;
			$start = int(($ccount - 1) / $size) * $size;
		} else {
			return 0;
		}
	} else {
		$topicid = $cgi->param('topicid');
	}

	# �����擾
	my $sqlcount = 
		'SELECT count(*)'.
		' FROM'.
		' topiccomments a,'.
		' users b,'.
		' forums c'.
		' WHERE'.
		' a.registuserid=b.userid'.
		' AND a.forumid=c.forumid'.
		' AND a.deleteflag=?'.
		' AND c.deleteflag=?'.
		' AND a.topicid=?'.
		' AND c.powerlevel<=?';
	my @bind = ('0', '0', $topicid, $session->param('powerlevel'));
	$commentcount = &selectFetch($dbh, $sqlcount, @bind);

	# �f�[�^������
	if ($commentcount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql =
			'SELECT'.
			' a.topiccommentid,'.
			' a.body,'.
			' a.registtime,'.
			' a.registuserid,'.
			' b.name'.
			' FROM topiccomments a,'.
			' users b,'.
			' forums c'.
			' WHERE'.
			' a.registuserid=b.userid'.
			' AND a.forumid=c.forumid'.
			' AND a.deleteflag=?'.
			' AND c.deleteflag=?'.
			' AND a.topicid=?'.
			' AND c.powerlevel<=?'.
			' ORDER BY a.registtime';
		if ($commentcount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		my @bind = ('0', '0', $topicid, $session->param('powerlevel'));
		@comments = &selectFetchArrayRef($dbh, $sql, @bind);
	}
}
