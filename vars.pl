use strict;
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use CGI;

require './global.pl';
require './jcode.pl';

# 設定読み込み
my %config = &getConfig;


###########################
# セッション有効時のテンプレート変数埋め込み
sub setCommonVars($) {
	my $tmpl = shift;
	my $session = shift;
	my $dbh = shift;

	my $cgi = &getCGI();
	my $phone = &getPhone();

	my $sidurl = undef;
	my $powerlevel = undef;
	if ($session) {
		$sidurl = $config{'sessionname'}.'='.$session->id;
		$powerlevel = $session->param('powerlevel');
	}
	if (!$powerlevel) {
		$powerlevel = 1;
	}

	my $isMobile = &isMobile();

	my $msg = '';

	# ユーザー名
	if ($tmpl->query(name => 'USER') eq 'VAR') {
		my $user = $cgi->param('user') || $cgi->cookie('user') or '';
		$tmpl->param(USER => &convertOutput($user));
	}
	# パスワード
	if ($tmpl->query(name => 'PASS') eq 'VAR') {
		my $pass = $cgi->param('pass') || '';
		$tmpl->param(PASS => &convertOutput($pass));
	}

	# ログインインフォメーション
	if ($session && $tmpl->query(name => 'INFO') eq 'VAR') {
		my $info = $session->param('info');
		$session->clear(['info']);
		$session->flush();
		if ($info) {
			$tmpl->param(INFO => $info);
		}
	}


	# タイトル
	if ($tmpl->query(name => 'TITLE') eq 'VAR') {
		$tmpl->param(TITLE => $config{'title'});
	}
	
	# サブタイトル
	if ($tmpl->query(name => 'SUBTITLE') eq 'VAR') {
		$tmpl->param(SUBTITLE => $config{'subtitle'});
	}
	
	# onjun お知らせメールアドレス
	if ($tmpl->query(name => 'ADMINMAIL') eq 'VAR') {
		$tmpl->param(ADMINMAIL => $config{'adminmail'});
	}
	
	# 自分の URL
	if ($tmpl->query(name => 'URL') eq 'VAR') {
		$tmpl->param(URL => $cgi->url(-relative=>1));
	}
	
	# 携帯端末
	if ($isMobile && $tmpl->query(name => 'MOBILE') eq 'VAR') {
		$tmpl->param(MOBILE => 1);
	}
	
	# ドコモ端末
	if ($phone->{type} eq "docomo" && $tmpl->query(name => 'DOCOMO') eq 'VAR') {
		$tmpl->param(DOCOMO => 1);
	}

	# セッション名
	if ($isMobile && $session && $tmpl->query(name => 'SESSIONNAME') eq 'VAR') {
		$tmpl->param(SESSIONNAME => $config{'sessionname'});
	}
	# セッション ID
	if ($isMobile && $session && $tmpl->query(name => 'SESSIONID') eq 'VAR') {
		$tmpl->param(SESSIONID => $session->id);
	}

	# トップページ URL
	if ($tmpl->query(name => 'URL_INDEX') eq 'VAR') {
		my $url = 'index.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_INDEX => &convertOutput($url));
	}

	# ユーザー登録の URL
	if ($tmpl->query(name => 'URL_REGUSER') eq 'VAR') {
		my $url = 'reguser.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_REGUSER => &convertOutput($url));
	}

	# 受信メッセージリストの URL
	if ($tmpl->query(name => 'URL_RECEIVEMESSAGELIST') eq 'VAR') {
		my $url = 'receivemessagelist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_RECEIVEMESSAGELIST => &convertOutput($url));
	}

	# 送信メッセージリストの URL
	if ($tmpl->query(name => 'URL_SENDMESSAGELIST') eq 'VAR') {
		my $url = 'sendmessagelist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SENDMESSAGELIST => &convertOutput($url));
	}

	# フォーラムの URL
	if ($tmpl->query(name => 'URL_FORUMLIST') eq 'VAR') {
		my $url = 'forumlist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_FORUMLIST => &convertOutput($url));
	}

	# 日記を書くの URL
	if ($tmpl->query(name => 'URL_WRITEDIARY') eq 'VAR') {
		my $url = 'writedialy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_WRITEDIARY => &convertOutput($url));
	}

	# 日記を読むの URL
	if ($tmpl->query(name => 'URL_READDIARY') eq 'VAR') {
		my $url = 'readdialy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_READDIARY => &convertOutput($url));
	}

	# メンバー一覧の URL
	if ($tmpl->query(name => 'URL_MEMBERLIST') eq 'VAR') {
		my $url = 'memberlist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_MEMBERLIST => &convertOutput($url));
	}

	# プロフィールの URL
	if ($tmpl->query(name => 'URL_PROFILE') eq 'VAR') {
		my $url = 'profile.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_PROFILE => &convertOutput($url));
	}

	# 設定変更の URL
	if ($tmpl->query(name => 'URL_OPTION') eq 'VAR') {
		my $url = 'option.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_OPTION => &convertOutput($url));
	}

	# 簡単ログイン設定の URL
	if ($tmpl->query(name => 'URL_SETEASY') eq 'VAR') {
		my $url = 'seteasy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SETEASY => &convertOutput($url));
	}

	# 集計の URL
	if ($tmpl->query(name => 'URL_ADDUP') eq 'VAR' && $powerlevel >= 5) {
		my $url = 'addup.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ADDUP => &convertOutput($url));
	}

	if ($tmpl->query(name => 'URL_SELFONTAMAIMAGE') eq 'VAR' || 
		$tmpl->query(name => 'SELFONTAMANAME') eq 'VAR' ||
		$tmpl->query(name => 'SELFONTAMAOWNERNAME') eq 'VAR') {
		if ($dbh && $session && $session->param('userid')) {
			# おんたま取得
			my %ontama = &getOntama($dbh, $session->param('userid'));
			# おんたま画像の URL
			if ($ontama{'image'} && $tmpl->query(name => 'URL_SELFONTAMAIMAGE') eq 'VAR') {
				my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
				$tmpl->param(URL_SELFONTAMAIMAGE => &convertOutput($url));
			}
			# おんたまの名前
			if ($ontama{'name'} && $tmpl->query(name => 'SELFONTAMANAME') eq 'VAR') {
				$tmpl->param(SELFONTAMANAME => &convertOutput($ontama{'name'}));
			}
			# おんたまの飼い主の名前
			if ($ontama{'ownername'} && $tmpl->query(name => 'SELFONTAMAOWNERNAME') eq 'VAR') {
				$tmpl->param(SELFONTAMAOWNERNAME => &convertOutput($ontama{'ownername'}));
			}

			# おんたま死亡フラグ
			if ($ontama{'health'} == 0 && $tmpl->query(name => 'SELFONTAMADEAD') eq 'VAR') {
				$tmpl->param(SELFONTAMADEAD => 1);
			}
		}
	}
	
	# おんたまの URL
	if ($tmpl->query(name => 'URL_ONTAMA') eq 'VAR') {
		my $url = 'ontama.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMA => &convertOutput($url));
	}

	# おんたま一覧の URL
	if ($tmpl->query(name => 'URL_ONTAMALIST') eq 'VAR') {
		my $url = 'ontamalist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMALIST => &convertOutput($url));
	}

	# おんたまマニュアルの URL
	if ($tmpl->query(name => 'URL_ONTAMAMANUAL') eq 'VAR') {
		my $url = 'ontamamanual.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMAMANUAL => &convertOutput($url));
	}

	# おんたま設定の URL
	if ($tmpl->query(name => 'URL_SETONTAMA') eq 'VAR') {
		my $url = 'setontama.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SETONTAMA => &convertOutput($url));
	}

	# ログアウトの URL
	if ($tmpl->query(name => 'URL_LOGOUT') eq 'VAR') {
		my $url = 'logout.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_LOGOUT => &convertOutput($url));
	}

	# ホームの URL
	if ($tmpl->query(name => 'URL_HOME') eq 'VAR') {
		my $url = 'home.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_HOME => &convertOutput($url));
	}

	# メール投稿確認の URL
	if ($tmpl->query(name => 'URL_RECEIVEMAIL') eq 'VAR') {
		my $url = 'receivemail.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_RECEIVEMAIL => &convertOutput($url));
	}

	# もっと新着情報の URL
	if ($tmpl->query(name => 'URL_NEWS') eq 'VAR') {
		my $url = 'news.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_NEWS => &convertOutput($url));
	}

	# 携帯機種情報
	if ($dbh && $session && $session->param('userid') && $tmpl->query(name => 'MOBCODE') eq 'VAR') {
		my $mobcode = &selectFetch($dbh, 'SELECT mobcode FROM users WHERE userid=? AND deleteflag=?', ($session->param('userid'), '0'));
		if ($mobcode) {
			$tmpl->param(MOBCODE => &convertOutput($mobcode));
		}
	}

	# フォーラム一覧
	if ($dbh && $tmpl->query(name => 'FORUMCATEGORIES') eq 'LOOP') {
		my @forumcategories = ();
		my $sql = 'SELECT forumcategoryid, name FROM forumcategories WHERE deleteflag=? AND powerlevel<=? order by orderno';
		my @bind = ('0', $powerlevel);
		my @categoriesrows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@categoriesrows) {
			my ($forumcategoryid, $name) = @$row;
			my %category = ();
			# フォーラムカテゴリ名
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'NAME']) eq 'VAR') {
				$category{'NAME'} = &convertOutput($name);
			}
			# フォーラムカテゴリID
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'ID']) eq 'VAR') {
				$category{'ID'} = $forumcategoryid;
			}
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS']) eq 'LOOP') {
				my @forums = ();
				my $sql = 'SELECT forumid, name, note FROM forums WHERE deleteflag=? AND forumcategoryid=? AND powerlevel<=? order by orderno';
				my @bind = ('0', $forumcategoryid, $powerlevel);
				my @forumsrows = &selectFetchArrayRef($dbh, $sql, @bind);
				foreach my $row(@forumsrows) {
					my ($forumid, $name, $note) = @$row;
					my %forum = ();
					# フォーラム名
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'NAME']) eq 'VAR') {
						$forum{'NAME'} = &convertOutput($name);
					}
					# フォーラム説明
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'NOTE']) eq 'VAR') {
						$forum{'NOTE'} = &convertOutput($note, 1);
					}
					# フォーラムURL
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL']) eq 'VAR') {
						my $url = 'forum.cgi?forumid='.$forumid;
						if ($isMobile && $session) {
							$url .= "&$sidurl";
						}
						$forum{'URL'} = &convertOutput($url);
					}
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL_LASTUSER']) eq 'VAR' || 
						$tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTUSER']) eq 'VAR' || 
						$tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTTIME']) eq 'VAR') {
						my $sql = 
							'SELECT a.lasttime, b.userid, b.name'.
							' FROM topics a, users b'.
							' WHERE a.lastuserid=b.userid AND a.deleteflag=? AND a.forumid=?'.
							' ORDER BY lasttime DESC LIMIT 0, 1';
						my @bind = ('0', $forumid);
						my ($lasttime, $userid, $username) = &selectFetchArray($dbh, $sql, @bind);
						# 最終投稿者URL
						if ($userid && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL_LASTUSER']) eq 'VAR') {
							my $url = 'profile.cgi?userid='.$userid;
							if ($isMobile && $session) {
								$url .= "&$sidurl";
							}
							$forum{'URL_LASTUSER'} = &convertOutput($url);
						}
						# 最終投稿者名
						if ($username && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTUSER']) eq 'VAR') {
							$forum{'LASTUSER'} = &convertOutput($username);
						}
						# 最終投稿時間
						if ($lasttime && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTTIME']) eq 'VAR') {
							$forum{'LASTTIME'} = $lasttime;
						}
					}
					# 話題数
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'THREADCOUNT']) eq 'VAR') {
						my $sql = 
							'SELECT count(*)'.
							' FROM topics'.
							' WHERE deleteflag=? AND forumid=?';
						my @bind = ('0', $forumid);
						my ($count) = &selectFetchArray($dbh, $sql, @bind);
						$forum{'THREADCOUNT'} = $count;
					}
					# 投稿数
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'POSTCOUNT']) eq 'VAR') {
						my $sql = 
							'SELECT count(*)'.
							' FROM topiccomments'.
							' WHERE deleteflag=? AND forumid=?';
						my @bind = ('0', $forumid);
						my ($count) = &selectFetchArray($dbh, $sql, @bind);
						$forum{'POSTCOUNT'} = $count;
					}
					push(@forums, \%forum);
				}
				$category{'FORUMS'} = \@forums;
			}
			push(@forumcategories, \%category);
		}
		$tmpl->param(FORUMCATEGORIES=> \@forumcategories);
	}

	# 新着一覧
	if ($dbh && $tmpl->query(name => 'NEWS') eq 'LOOP') {
		my @newsvars = ();
		my $sql = 
			'SELECT'.
			' a.forumid,'.
			' d.name,'.
			' a.topicid,'.
			' a.title,'.
			' a.lastcommentid,'.
			' a.lastuserid,'.
			' c.name,'.
			' a.lasttime,'.
			' a.commentcount'.
			' FROM'.
			' topics a,'.
			' users c,'.
			' forums d'.
			' WHERE'.
			' a.lastuserid=c.userid AND'.
			' a.forumid=d.forumid AND'.
			' a.deleteflag=? AND'.
			' d.deleteflag=? AND'.
			' d.powerlevel<=?'.
			' ORDER BY a.lasttime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', '0', $powerlevel);
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($forumid, $forumname, $topicid, $title, $lastcommentid, $lastuserid, $lastusername, $lasttime, $commentcount) = @$row;
			my %newsvar = ();
			# 時間
			if ($tmpl->query(name => ['NEWS', 'TIME']) eq 'VAR') {
				$newsvar{'TIME'} = &convertOutput($lasttime);
			}
			# 日付
			if ($tmpl->query(name => ['NEWS', 'DATE']) eq 'VAR') {
				if ($lasttime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newsvar{'DATE'} = &convertOutput($2.'月'.$3.'日');
				}
			}
			# トピックタイトル
			if ($tmpl->query(name => ['NEWS', 'TOPICTITLE']) eq 'VAR') {
				$newsvar{'TOPICTITLE'} = &convertOutput($title);
			}
			# トピックURL
			if ($tmpl->query(name => ['NEWS', 'URL']) eq 'VAR') {
				my $url = 'topic.cgi?';
				if ($lastcommentid) {
					$url .= 'topiccommentid='.$lastcommentid;
				} else {
					$url .= 'topicid='.$topicid;
				}
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				if ($lastcommentid) {
					$url .= '#'.$lastcommentid;
				}
				$newsvar{'URL'} = &convertOutput($url);
			}
			# トピックコメント数
			if ($tmpl->query(name => ['NEWS', 'COUNT']) eq 'VAR') {
				$newsvar{'COUNT'} = &convertOutput($commentcount);
			}
			# フォーラム名
			if ($tmpl->query(name => ['NEWS', 'FORUMNAME']) eq 'VAR') {
				$newsvar{'FORUMNAME'} = &convertOutput($forumname);
			}
			# フォーラムURL
			if ($tmpl->query(name => ['NEWS', 'FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?topicid='.$topicid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$url .= '#'.$topicid;
				$newsvar{'FORUMURL'} = &convertOutput($url);
			}
			# 最終投稿者
			if ($tmpl->query(name => ['NEWS', 'LASTUSERNAME']) eq 'VAR') {
				$newsvar{'LASTUSERNAME'} = &convertOutput($lastusername);
			}
			# 最終投稿者URL
			if ($tmpl->query(name => ['NEWS', 'LASTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$lastuserid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$newsvar{'LASTUSERURL'} = &convertOutput($url);
			}
			push(@newsvars, \%newsvar);
		}
		$tmpl->param(NEWS=> \@newsvars);
	}

	# 新着メッセージの件数
	if ($dbh && $session && $session->param('userid') && $tmpl->query(name => 'NEW_MESSAGE_COUNT') eq 'VAR') {
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE receiver_userid=? AND receiver_deleteflag=? AND opentime IS NULL', ($session->param('userid'), '0'));
		if ($count) {
			$tmpl->param(NEW_MESSAGE_COUNT => $count);
		}
	}

	# 新しく登録したメンバー一覧
	if ($dbh && $tmpl->query(name => 'NEWMEMBERS') eq 'LOOP') {
		my @newmembersvars = ();
		my $sql = 
			'SELECT'.
			' userid,'.
			' name,'.
			' registtime'.
			' FROM'.
			' users'.
			' WHERE'.
			' deleteflag=?'.
			' AND registtime >= DATE_ADD(CURRENT_DATE, INTERVAL ? MONTH)'.
			' ORDER BY registtime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', -1);
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($userid, $name, $registtime) = @$row;
			my %newmembersvar = ();
			# 時間
			if ($tmpl->query(name => ['NEWMEMBERS', 'TIME']) eq 'VAR') {
				$newmembersvar{'TIME'} = &convertOutput($registtime);
			}
			# 日付
			if ($tmpl->query(name => ['NEWMEMBERS', 'DATE']) eq 'VAR') {
				if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newmembersvar{'DATE'} = &convertOutput($2.'月'.$3.'日');
				}
			}
			# 名前
			if ($tmpl->query(name => ['NEWMEMBERS', 'NAME']) eq 'VAR') {
				$newmembersvar{'NAME'} = &convertOutput($name);
			}
			# メンバーURL
			if ($tmpl->query(name => ['NEWMEMBERS', 'URL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$newmembersvar{'URL'} = &convertOutput($url);
			}
			push(@newmembersvars, \%newmembersvar);
		}
		$tmpl->param(NEWMEMBERS => \@newmembersvars);
	}


	# 現在オンラインのメンバー一覧
	if ($dbh && $tmpl->query(name => 'ONLINEMEMBERS') eq 'LOOP') {
		my @onlinemembersvars = ();
		my $sql = 
			'SELECT'.
			' a.userid,'.
			' a.name,'.
			' b.registtime,'.
			' b.title'.
			' FROM'.
			' users a,'.
			' onlineusers b'.
			' WHERE'.
			' a.userid=b.userid'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?'.
			' ORDER BY registtime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', '0');
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($userid, $name, $registtime, $title) = @$row;
			my %onlinemembersvar = ();
			# 名前
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'NAME']) eq 'VAR') {
				$onlinemembersvar{'NAME'} = &convertOutput($name);
			}
			# メンバーURL
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'URL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$onlinemembersvar{'URL'} = &convertOutput($url);
			}
			# メンバーURL
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'PAGETITLE']) eq 'VAR') {
				$onlinemembersvar{'PAGETITLE'} = &convertOutput($title);
			}
			push(@onlinemembersvars, \%onlinemembersvar);
		}
		$tmpl->param(ONLINEMEMBERS => \@onlinemembersvars);
	}


	return $msg;
}


1;
