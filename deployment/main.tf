terraform{
    required_providers {
        render = {
            source = "render-oss/render"
            version = "1.9.1"
        }
    }
}

resource "render_web_service" "web" {
  name               = "terraform-web-service"
  plan               = "free"
  region             = "oregon"

  runtime_source = {
    image = {
      image_url = "docker.io/guysadev/api-mock:0.1.0 "
    }
  }

}