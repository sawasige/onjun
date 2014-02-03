#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
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

#プログラム開始
&main;

##########
# メイン
sub main {
	$cgi = new CGI;
	$msg = '';

	# 設定読み込み
	%config = &config;

	# セッション読み込み
	$session = &readSession(1);
	if (defined $session) {
		$sid = $session->id;

		# DB オープン
		$dbh = &connectDB(1);

		# コメント一覧取得
		&getCommentList();

		# 現在の画面
		$msg .= &checkOnline($dbh, $session->param('userid'), 'トピック');

		# 画面表示
		&disp;

		# DB クローズ
		&disconnectDB($dbh);
	}
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	my $tmpl = &readTemplate($cgi);

	# 共通テンプレート変数セット
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# メッセージ
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	

	# コメントを書くURL
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

		# フォーラム名
		if ($name && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($name));
		}
		# フォーラム説明
		if ($note && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($note, 1));
		}
		# フォーラムURL
		if ($name && $tmpl->query(name => ['FORUMURL']) eq 'VAR') {
			my $url = 'forum.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(FORUMURL => &convertOutput($url));
		}
		# 新規トピック作成URL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
		}
		# トピックID
		if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
			$tmpl->param(TOPICID => $topicid);
		}
		# トピックタイトル
		if ($title && $tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($title));
		}
		# トピックタイトル
		if ($title && $tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($title));
		}
		# トピック本文
		if ($body && $tmpl->query(name => ['TOPICBODY']) eq 'VAR') {
			$tmpl->param(TOPICBODY => &convertOutput($body, 1));
		}
		# 登録時間
		if ($registtime && $tmpl->query(name => ['TOPICREGISTTIME']) eq 'VAR') {
			$tmpl->param(TOPICREGISTTIME => $registtime);
		}
		# 登録者
		if ($registusername && $tmpl->query(name => ['TOPICREGISTUSERNAME']) eq 'VAR') {
			$tmpl->param(TOPICREGISTUSERNAME => &convertOutput($registusername));
		}
		# 登録者URL
		if ($registuserid && $tmpl->query(name => ['TOPICREGISTUSERURL']) eq 'VAR') {
			my $url = 'profile.cgi?userid='.$registuserid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICREGISTUSERURL => &convertOutput($url));
		}
		# トピック修正URL
		if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['MODIFYTOPICURL']) eq 'VAR') {
			my $url = 'modifytopic.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MODIFYTOPICURL => &convertOutput($url));
		}
		# トピック削除URL
		if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['DELETETOPICURL']) eq 'VAR') {
			my $url = 'deletetopicconfirm.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(DELETETOPICURL => &convertOutput($url));
		}

		# 添付ファイル1
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

		# 添付ファイル2
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

		# 添付ファイル3
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

	# コメント一覧
	if (@comments && $tmpl->query(name => 'COMMENTS') eq 'LOOP') {
		my @commentvars = ();
		my $commentno = $start + 1;
		foreach my $row(@comments) {
			my ($topiccommentid, $body, $registtime, $registuserid, $registusername) = @$row;
			my %commentvar;
			# コメント連番
			if ($tmpl->query(name => ['COMMENTS', 'COMMENTNO']) eq 'VAR') {
				$commentvar{'COMMENTNO'} = &convertOutput($commentno);
			}
			$commentno++;
			# コメントID
			if ($tmpl->query(name => ['COMMENTS', 'ID']) eq 'VAR') {
				$commentvar{'ID'} = &convertOutput($topiccommentid);
			}
			# コメント
			if ($tmpl->query(name => ['COMMENTS', 'BODY']) eq 'VAR') {
				$commentvar{'BODY'} = &convertOutput($body, 1);
			}
			# コメント登録時間
			if ($tmpl->query(name => ['COMMENTS', 'REGISTTIME']) eq 'VAR') {
				$commentvar{'REGISTTIME'} = $registtime;
			}
			# コメント登録者
			if ($tmpl->query(name => ['COMMENTS', 'REGISTUSERNAME']) eq 'VAR') {
				$commentvar{'REGISTUSERNAME'} = &convertOutput($registusername);
			}
			# コメント登録者URL
			if ($tmpl->query(name => ['COMMENTS', 'REGISTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$registuserid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'REGISTUSERURL'} = &convertOutput($url);
			}
			# コメントURL
			if ($tmpl->query(name => ['COMMENTS', 'TOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'topiccomment.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'TOPICCOMMENTURL'} = &convertOutput($url);
			}
			# コメント修正URL
			if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['COMMENTS', 'MODIFYTOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'modifytopiccomment.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'MODIFYTOPICCOMMENTURL'} = &convertOutput($url);
			}
			# コメント修正URL
			if (($session->param('userid') eq $registuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['COMMENTS', 'DELETETOPICCOMMENTURL']) eq 'VAR') {
				my $url = 'deletetopiccommentconfirm.cgi?topiccommentid='.$topiccommentid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'DELETETOPICCOMMENTURL'} = &convertOutput($url);
			}

			my $existfile = 0;
			# 添付ファイル1
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
			# 添付ファイル2
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
			# 添付ファイル3
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
			# 添付ファイルの有無
			if ($existfile && $tmpl->query(name => ['COMMENTS', 'EXISTFILE']) eq 'VAR') {
				$commentvar{'EXISTFILE'} = 1;
			}

			# 携帯端末
			if (&isMobile && $tmpl->query(name => ['COMMENTS', 'MOBILE']) eq 'VAR') {
				$commentvar{'MOBILE'} = 1;
			}

			push(@commentvars, \%commentvar);
		}
		$tmpl->param(COMMENTS => \@commentvars);
	}

	# 前ページ
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

	# 前ページ番号
	if ($start > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		# 9 ページ以上は移動できない
		my $startno = $no - 9;
		if ($startno < 1) {
			$startno = 1;
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = &getCondUrl();
			# 開始行
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

	# 次ページ
	if (($start + @comments) < $commentcount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = &getCondUrl();
		$url .= '&start='.$nextstart;
		$url .= '&size='.$size;
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# 次ページ番号
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
			# 開始行
			$url .= '&start='.($i-1) * $size;
			$url .= '&size='.$size;
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 9 ページ以上は移動できない
			if (@pagedata >= 9) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# 現在ページ
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		# ページ処理する場合だけ表示
		if ($size < $commentcount) {
			my $no = int($start / $size) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}

	# メッセージ（あれば）
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# 検索条件を URL エンコード
sub getCondUrl {
	my $url = $cgi->url(-relative=>1).'?';
	$url .= 'topicid='.$topicid;
	# セッション
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	return $url;
}

#####################
# コメント一覧取得
sub getCommentList() {
	$commentcount = 0;
	@comments = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# コメントが指定されている場合は topicid を探す
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

	# 件数取得
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

	# データがある
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
