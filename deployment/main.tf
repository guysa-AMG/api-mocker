terraform{
    required_providers {
        render = {
            source = "render-oss/render"
            version = "1.9.1"
        }
    }
}
provider "render" {
owner_id = "tea-dag5du2jnfac73boneog" 
   
}
resource "render_web_service" "web" {
  name               = "terraform-web-service"
  plan               = "free"
  region             = "oregon"



  runtime_source = {
    image = {
      image_url = "docker.io/guysadev/api-mock"
      tag       = "0.1.0"
     
    }
  }

}
