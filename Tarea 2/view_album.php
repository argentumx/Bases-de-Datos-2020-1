<?php 
include("includes/header.php");
if(isset($_GET['id']) and isset($_GET['cur'])) {
	$album_id = $_GET['id'];
	$is_current = $_GET['cur'];
}
else {
	header("Location: index.php");
	exit();
}

// Se trabaja sobre la vista que contiene canciones asociadas a cada album, con su nombre, artista y duracion.
// Ademas, la vista contiene nombre de album y se fecha de publicacion.
$duracion_album = mysqli_query($connection, "SELECT SUM(duracion) FROM vista_album WHERE id_album='$album_id'");
$fila = mysqli_fetch_row($duracion_album);
$duracion_album = $fila[0];
$s = $duracion_album % 60;
$min = ($duracion_album - $s)/60;

$query = mysqli_query($connection, "SELECT * FROM vista_album WHERE id_album='$album_id'");
$total_canciones = mysqli_num_rows($query);
$fila = mysqli_fetch_row($query);

if($fila) {
	$year = $fila[3];
	$album_name = $fila[5];
	$aid = $fila[6];
	$artist = $fila[2];
}
// Album en cuestion esta vacio. Se obtienen manualmente sus datos, pues no esta en la vista.
else {
	$query_aux = mysqli_query($connection, "SELECT nombre, id_artista, debut_year FROM albumes WHERE id_album='$album_id'");
	$fila2 = mysqli_fetch_row($query_aux);
	$album_name = $fila2[0];
	$year = $fila2[2];
	$aid =  $fila2[1];
	$query_aux = mysqli_query($connection, "SELECT nombre FROM personas WHERE id_persona='$aid'");
	$fila2 = mysqli_fetch_row($query_aux);
	$artist = $fila2[0];
}

?>
<div class="entityinfo">
	<div class="leftsection">
		<img src="img/album1.png" style="width: 100%"/>
	</div>
	<div class="rightsection">
		<h2 class='title mb-3' style="margin-top: 0px"><?php echo $album_name ?></h2>
		<?php echo "<a style='text-decoration:none;' href='artist_profile.php?id=".$aid."&&cur=".$is_current."'><p style='color:#b3b3b3; font-weight: 500; margin-bottom: 0px;text-decoration:none;'>Por ".$artist."</p></a>";
		?>
		<p style="color:#b3b3b3; font-weight: 400; margin-top: 3px;"><?php echo $total_canciones ?> canciones</p>
		<p style="color:#b3b3b3; font-weight: 400; margin-top: 90px;"><?php echo $min ?> min <?php echo $s?> s</p>
		<p style="color:#b3b3b3; font-weight: 400;"><?php echo $year ?></p>
	</div>
	<?php
	if($is_current){
		echo
		"<a href='album_edit.php?id=".$album_id."&&cur=".$is_current."'style='float:right; text-decoration:none;'>
			<button class='x-button' type='submit'>Editar el album</button>
		</a>";
	}
	?>
</div>


<div class="tracklist-container">
	<ul class="tracklist" style='padding:0'>
<?php
	while($fila) {
		$nombre_cancion = $fila[0];
		$duracion = $fila[1];
		$s = $duracion % 60;
		$min = ($duracion - $s)/60;
		$year = $fila[3];
		$album_name = $fila[5];
		$artist = $fila[2];
		$cancion_id = $fila[7];
		$fila = mysqli_fetch_row($query);

		echo 
		"<li class='track'>
			<img class='note' src = 'img/note.png'/>
			<img class='playbutton' src='img/play.png'/>
			<div class='trackinfo'>
				<span class='trackname' style='font-size:17px;'>".$nombre_cancion."</span>
				<span class='trackname' style='color:#b3b3b3; font-weight:400;'>".$artist."</span>

			</div>
			<div class='track-options'>
				<input type='hidden' id='id_cancion' class='cid' value='".$cancion_id."'>
				<button onclick='showOptionsMenu(this)'><img class='optbutton' src='img/dots.png'></button>
			</div>

			<div class='track-duration'>
				<span class='trackdur'>".$min.":".$s."</span>
			</div>
		</li>";
	}

?>
	
		
	</ul>
</div>

<nav class='optMenu'>
	<input type="hidden" class="cid">
	<?php
	// soy artista de este album y no existen colaboraciones
		if($is_current){
			// entonces debo poder sacar la cancion de album
			echo "<div class='item' onclick='deleteFromAlbum(this, ".$_GET['id'].")'> Borrar de álbum </div>";
			// entonces debo poder agregarla a otro album
			echo
				"<select class='item' onchange='addToAlbum(this)'>
					<option value='' style=''>Agregar a otro álbum</option>";
				$query = mysqli_query($connection, "SELECT * FROM albumes WHERE id_artista=".$_SESSION['id']);
				$fila = mysqli_fetch_row($query);
				while($fila){
					$alid = $fila[0];
					$nombre = $fila[2];
					echo "<option value='".$alid."'>".$nombre."</option>";
					$fila = mysqli_fetch_row($query);
				}
				echo "</select>";
			// y debo poder editarla tambien
			echo "<div class='item' onclick='editSong(this)'> Editar la canción</div>";
		}
		else{
			// soy usuario, solo puedo dar likes y agregar a playlists
			echo "<div class='item' id='like'></div>";
			echo
				"<select class='item' onchange='addToPlaylist(this)'>
					<option value=''>Agregar a playlist</option>";
				$query = mysqli_query($connection, "SELECT * FROM playlists WHERE id_usuario=".$_SESSION['id']);
				$fila = mysqli_fetch_row($query);
				while($fila){
					$pid = $fila[0];
					$nombre = $fila[2];
					echo "
					<form action='includes/album.inc.php' method='post'>
					<button name='add_toalbum'><option value='".$pid."'>".$nombre."</option></button>";
					$fila = mysqli_fetch_row($query);
				}
				echo "</select>";
		}
	?>

</nav>



<?php include("includes/footer.php")?>