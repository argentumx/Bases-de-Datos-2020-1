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
		<h2 class='title mb-3' style="margin-top: 0px">
			<?php
			if($is_current){
				echo
				"<form action='includes/album.inc.php' method='post' style='width:600px;'>
					<div class='form-input' style='display:flex; margin:0;'>
					<input type='text' name='name' placeholder='Nuevo nombre' style='display:flex; margin-right:50px; background: #282828; height: 40px; font-weight: 600; font-size: 20px; padding-left: 20px; color: #fff;'>
					<button class='x-button'type='submit' name='change_albumname'>Guardar</button>
					</div>
					<input type='hidden' name='to-change' value='".$album_id."'>
					<input type='hidden' name='is_cur' value='".$is_current."'>";
					echo
				"<form action='includes/album.inc.php' method='post' style='width:600px;'>
					<div class='form-input' style='display:flex; margin:0;'>
					<input type='text' name='year' placeholder='Nuevo año de estreno' style='display:flex; margin-right:50px; background: #282828; height: 40px; font-weight: 600; font-size: 20px; padding-left: 20px; color: #fff; width:250px;'>
					<button class='x-button'type='submit' name='change_albumyear' style='margin-left:185px;'>Guardar</button>
					</div>
					<input type='hidden' name='to-change' value='".$album_id."'>
					<input type='hidden' name='is_cur' value='".$is_current."'>";
			}
			?>
		</h2>
		<?php echo "<a style='text-decoration:none;' href='artist_profile.php?id=".$aid."&&cur=".$is_current."'><p style='color:#b3b3b3; font-weight: 500; margin-bottom: 0px;text-decoration:none;'>Por ".$artist."</p></a>";
		?>
		<p style="color:#b3b3b3; font-weight: 400; margin-top: 3px;"><?php echo $total_canciones ?> canciones</p>
		<p style="color:#b3b3b3; font-weight: 400; margin-top: 90px;"><?php echo $min ?> min <?php echo $s?> s</p>
		<?php 
		echo 
		"<form action='includes/album.inc.php' method='post' style='float:left;'>
			<input type='hidden' name='to-delete' value='".$album_id."'>
			<button class='x-button' style='float:left;' name='delete_album' type='submit'>Borrar</button>
		</form>

		<a href='view_album.php?id=".$album_id."&&cur=".$is_current."'style='float:right; text-decoration:none; margin-top:3px;'>
			<button class='x-button'type='submit'>Dejar de editar</button>
		</form>";
	?>
	</div>
</div>



<?php include("includes/footer.php")?>