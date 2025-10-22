// Minimal region→comuna population script to avoid conflicts with inline validation.
(function(){
  const REGION_COMMUNES = [
    { name: "Arica y Parinacota", comunas: ["Arica","Camarones","Putre","General Lagos"] },
    { name: "Tarapacá", comunas: ["Iquique","Alto Hospicio","Pozo Almonte","Camiña","Colchane","Huara","Pica"] },
    { name: "Antofagasta", comunas: ["Antofagasta","Mejillones","Sierra Gorda","Taltal","Calama","Ollagüe","San Pedro de Atacama","Tocopilla","María Elena"] },
    { name: "Atacama", comunas: ["Copiapó","Caldera","Tierra Amarilla","Chañaral","Diego de Almagro","Vallenar","Freirina","Huasco","Alto del Carmen"] },
    { name: "Coquimbo", comunas: ["La Serena","Coquimbo","Andacollo","La Higuera","Paihuano","Vicuña","Illapel","Canela","Los Vilos","Salamanca","Ovalle","Combarbalá","Monte Patria","Punitaqui","Río Hurtado"] },
    { name: "Valparaíso", comunas: ["Valparaíso","Casablanca","Concón","Juan Fernández","Puchuncaví","Quilpué","Quintero","Villa Alemana","Viña del Mar","Rapa Nui (Isla de Pascua)","Los Andes","Calle Larga","Rinconada","San Esteban","La Ligua","Cabildo","Papudo","Petorca","Zapallar","Quillota","La Calera","Hijuelas","La Cruz","Nogales","Limache","Olmué","San Antonio","Algarrobo","Cartagena","El Quisco","El Tabo","Santo Domingo","San Felipe","Catemu","Llay-Llay","Panquehue","Putaendo","Santa María"] },
    { name: "Metropolitana de Santiago", comunas: ["Cerrillos","Cerro Navia","Conchalí","El Bosque","Estación Central","Huechuraba","Independencia","La Cisterna","La Florida","La Granja","La Pintana","La Reina","Las Condes","Lo Barnechea","Lo Espejo","Lo Prado","Macul","Maipú","Ñuñoa","Pedro Aguirre Cerda","Peñalolén","Providencia","Pudahuel","Quilicura","Quinta Normal","Recoleta","Renca","San Joaquín","San Miguel","San Ramón","Santiago","Vitacura","Colina","Lampa","Tiltil","Puente Alto","Pirque","San José de Maipo","San Bernardo","Buin","Calera de Tango","Paine","Melipilla","Alhué","Curacaví","María Pinto","San Pedro","Talagante","El Monte","Isla de Maipo","Padre Hurtado","Peñaflor"] },
    { name: "O'Higgins", comunas: ["Rancagua","Codegua","Coinco","Coltauco","Doñihue","Graneros","Las Cabras","Machalí","Malloa","Mostazal","Olivar","Peumo","Pichidegua","Quinta de Tilcoco","Rengo","Requínoa","San Vicente","Pichilemu","La Estrella","Litueche","Marchihue","Navidad","Paredones","San Fernando","Chépica","Chimbarongo","Lolol","Nancagua","Palmilla","Peralillo","Placilla","Pumanque","Santa Cruz"] },
    { name: "Maule", comunas: ["Talca","Constitución","Curepto","Empedrado","Maule","Pelarco","Pencahue","Río Claro","San Clemente","San Rafael","Cauquenes","Chanco","Pelluhue","Curicó","Hualañé","Licantén","Molina","Rauco","Romeral","Sagrada Familia","Teno","Vichuquén","Linares","Colbún","Longaví","Parral","Retiro","San Javier","Villa Alegre","Yerbas Buenas"] },
    { name: "Ñuble", comunas: ["Bulnes","Chillán","Chillán Viejo","El Carmen","Pemuco","Pinto","Quillón","San Ignacio","Yungay","Cobquecura","Coelemu","Ninhue","Portezuelo","Quirihue","Ránquil","Trehuaco","Coihueco","Ñiquén","San Carlos","San Fabián","San Nicolás"] },
    { name: "Biobío", comunas: ["Concepción","Coronel","Chiguayante","Florida","Hualpén","Hualqui","Lota","Penco","San Pedro de la Paz","Santa Juana","Talcahuano","Tomé","Arauco","Cañete","Contulmo","Curanilahue","Lebu","Los Álamos","Tirúa","Los Ángeles","Alto Biobío","Antuco","Cabrero","Laja","Mulchén","Nacimiento","Negrete","Quilaco","Quilleco","San Rosendo","Santa Bárbara","Tucapel","Yumbel"] },
    { name: "La Araucanía", comunas: ["Temuco","Carahue","Cholchol","Cunco","Curarrehue","Freire","Galvarino","Gorbea","Lautaro","Loncoche","Melipeuco","Nueva Imperial","Padre Las Casas","Perquenco","Pitrufquén","Pucón","Saavedra","Teodoro Schmidt","Toltén","Vilcún","Villarrica","Angol","Collipulli","Curacautín","Ercilla","Lonquimay","Los Sauces","Lumaco","Purén","Renaico","Traiguén","Victoria"] },
    { name: "Los Ríos", comunas: ["Valdivia","Corral","Lanco","Los Lagos","Máfil","Mariquina","Paillaco","Panguipulli","La Unión","Futrono","Lago Ranco","Río Bueno"] },
    { name: "Los Lagos", comunas: ["Ancud","Castro","Chonchi","Curaco de Vélez","Dalcahue","Puqueldón","Queilén","Quemchi","Quellón","Quinchao","Calbuco","Cochamó","Fresia","Frutillar","Llanquihue","Los Muermos","Maullín","Puerto Montt","Puerto Varas","Osorno","Puerto Octay","Purranque","Puyehue","Río Negro","San Juan de la Costa","San Pablo","Chaitén","Futaleufú","Hualaihué","Palena"] },
    { name: "Aysén", comunas: ["Coyhaique","Lago Verde","Aysén","Cisnes","Guaitecas","Cochrane","O'Higgins","Tortel","Chile Chico","Río Ibáñez"] },
    { name: "Magallanes y la Antártica Chilena", comunas: ["Punta Arenas","Laguna Blanca","Río Verde","San Gregorio","Porvenir","Primavera","Timaukel","Cabo de Hornos (Puerto Williams)","Antártica","Natales","Torres del Paine"] }
  ];

  function normalizeText(v){
    return (v||'').toString().trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
  }

  function populate(){
    const region = document.querySelector('select[name="region"]');
    const comuna = document.querySelector('select[name="comuna"]');
    if(!region || !comuna) return;
    
    const map = new Map(REGION_COMMUNES.map(r=>[normalizeText(r.name), r.comunas]));
    
    const initialComunaValue = comuna.value;

    function fill(regionValue, preserveSelection = false){
      const comunaToSelect = preserveSelection ? comuna.value : '';
      
      const comunas = map.get(normalizeText(regionValue)) || [];
      comuna.innerHTML = '';
      
      const ph = document.createElement('option');
      ph.value = '';
      ph.textContent = comunas.length ? 'Selecciona una comuna' : 'Selecciona una región primero';
      ph.disabled = true; 
      ph.hidden = true;
      comuna.appendChild(ph);
      
      let hasSelection = false;
      comunas.forEach(c=>{
        const opt = document.createElement('option');
        opt.value = c; 
        opt.textContent = c;
        if (comunaToSelect && c === comunaToSelect) {
          opt.selected = true;
          hasSelection = true;
        }
        comuna.appendChild(opt);
      });
      
      if (!hasSelection && preserveSelection && initialComunaValue) {
        const opts = comuna.querySelectorAll('option');
        opts.forEach(opt => {
          if (opt.value === initialComunaValue) {
            opt.selected = true;
            hasSelection = true;
          }
        });
      }
      
      comuna.disabled = comunas.length === 0;
      
      comuna.dispatchEvent(new Event('change', { bubbles: true }));
      
      if(typeof window.updateSubmitButton === 'function'){
        try{ window.updateSubmitButton(); }catch(_){ }
      }
    }

    fill(region.value, true);
    
    region.addEventListener('change', e=> {
      fill(e.target.value, false);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', populate);
  } else {
    populate();
  }
})();
