<div class="topbar">
	<div class="botones-nav">
		<button type="button">
			<a href="followed_users.php">Usuarios que sigo</a>
		</button>
		<button type="button">
			<a href="followed_artists.php">Artistas que sigo</a>
		</button>
		<button type="button">
			<a href="followed_playlists.php">Playlists que sigo</a>
		</button>
	</div>
	<div class="dropdown menu ml-3"style="width: 100px; position: absolute; right:3%; margin-right: 28px; top: 10px;">
		<button type="button" class="d-flex align-items-center" data-toggle="dropdown">
			<?php if($_SESSION['usertype'] == 'user'):?>
				<img src="img/user_profile.png" class="profile" width=150px>
			<?php else: ?>
				<img src="img/artist_profile.png" class="profile" width=150px>
			<?php endif; ?>
			<span><?php echo $_SESSION['nombre'];?></span>
				<i class="fas fa-caret-down ml-2 mr-2"></i>
		</button>
		<div class="dropdown-menu mt-0 p-0">
				<a href="account.php" class="dropdown-item">Cuenta</a>
				<?php if($_SESSION['usertype'] == 'artist'){
					echo "<a href='artist_profile.php?id=".$_SESSION['id']."&&cur=".true."'class='dropdown-item'>Perfil</a>";

				}
				else{
					echo "<a href='user_profile.php?id=".$_SESSION['id']."&&cur=".true."'class='dropdown-item'>Perfil</a>";
				}
				?>
				<div class="dropdown-divider"></div>
				<a name="logout-submit" href="includes/logout.inc.php" class="dropdown-item">Salir</a> 
		</div>
	</div>
</div>